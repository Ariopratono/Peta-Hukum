# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ConsolidationWizard(models.TransientModel):
    _name = 'consolidation.wizard'
    _description = 'Wizard untuk Menggabungkan Peraturan'

    name = fields.Char(
        string='Nama Konsolidasi',
        required=True,
        help='Beri nama hasil konsolidasi, misal: UU ITE Terpadu (2008-2024)'
    )
    
    description = fields.Text(
        string='Deskripsi',
        help='Deskripsi singkat tentang konsolidasi ini'
    )
    
    regulation_ids = fields.Many2many(
        'legal.regulation',
        string='Peraturan yang Akan Digabung',
        required=True,
        help='Pilih UU Induk dan semua UU perubahannya (akan diurutkan otomatis berdasarkan tahun)'
    )
    
    display_mode = fields.Selection([
        ('annotated', 'Mode Anotasi (Tampilkan Perubahan)'),
        ('final', 'Mode Final (Versi Terbaru Saja)'),
        ('history', 'Mode Riwayat (Semua Versi)'),
        ('comparison', 'Mode Perbandingan (Side by Side)')
    ], string='Mode Tampilan', default='annotated', required=True,
       help='Pilih bagaimana hasil konsolidasi akan ditampilkan')

    auto_save_as_new = fields.Boolean(
        string='Simpan sebagai Peraturan Baru',
        default=True,
        help='Jika dicentang, hasil konsolidasi akan disimpan sebagai peraturan baru dengan tipe "Naskah Kompilasi"'
    )

    @api.model
    def default_get(self, fields_list):
        """Pre-fill dengan peraturan yang dipilih dari tree view"""
        res = super(ConsolidationWizard, self).default_get(fields_list)
        
        # Get active IDs dari context
        if self._context.get('active_ids'):
            res['regulation_ids'] = [(6, 0, self._context.get('active_ids', []))]
            
            # Generate default name
            regs = self.env['legal.regulation'].browse(self._context.get('active_ids', []))
            if regs:
                first_reg = regs.sorted(key=lambda r: (r.tahun, r.nomor))[0]
                years = sorted(set([r.tahun for r in regs]))
                year_range = f"{years[0]}-{years[-1]}" if len(years) > 1 else str(years[0])
                res['name'] = f"{first_reg.bentuk_singkat or 'UU'} Terpadu ({year_range})"
        
        return res

    def action_generate_consolidation(self):
        """Generate konsolidasi dan tampilkan hasilnya"""
        self.ensure_one()
        
        if not self.regulation_ids:
            raise UserError(_('Pilih minimal satu peraturan untuk digabung.'))
        
        if len(self.regulation_ids) < 2:
            raise UserError(_(
                'Untuk konsolidasi, pilih minimal dua peraturan:\n'
                '1. UU Induk (versi asli)\n'
                '2. UU Perubahan (versi yang mengubah UU Induk)\n\n'
                'Contoh: UU 11/2008 dan UU 19/2016'
            ))
        
        # Create consolidation record
        consolidation = self.env['legal.regulation.consolidation'].create({
            'name': self.name,
            'description': self.description,
            'regulation_ids': [(6, 0, self.regulation_ids.ids)],
            'display_mode': self.display_mode,
        })
        
        # Generate consolidation
        consolidation.action_generate_consolidation()
        
        # If auto_save_as_new, create a new regulation record
        if self.auto_save_as_new:
            sorted_regs = self.regulation_ids.sorted(key=lambda r: (r.tahun, r.nomor))
            base_reg = sorted_regs[0]
            latest_reg = sorted_regs[-1]
            
            new_regulation = self.env['legal.regulation'].create({
                'judul': f'{self.name} - Naskah Konsolidasi',
                'tipe_dokumen': base_reg.tipe_dokumen,
                'teu': base_reg.teu,
                'nomor': f'KONSOLIDASI-{base_reg.nomor}',
                'bentuk': base_reg.bentuk,
                'bentuk_singkat': base_reg.bentuk_singkat,
                'tahun': latest_reg.tahun,
                'tempat_penetapan': base_reg.tempat_penetapan,
                'tanggal_penetapan': latest_reg.tanggal_penetapan,
                'tanggal_pengundangan': latest_reg.tanggal_pengundangan,
                'tanggal_berlaku': latest_reg.tanggal_berlaku,
                'sumber': f'Konsolidasi dari {len(self.regulation_ids)} peraturan',
                'subjek': base_reg.subjek,
                'status': 'berlaku',
                'bahasa': base_reg.bahasa,
                'bidang': base_reg.bidang,
                'isi_peraturan': consolidation.consolidated_html,
                'regulation_type': 'consolidated',
                'source_regulation_ids': [(6, 0, self.regulation_ids.ids)],
                'description': self.description,
                'keterangan': f'Dibuat otomatis dari wizard konsolidasi pada {fields.Datetime.now()}'
            })
            
            # Return action to open the new regulation
            return {
                'name': _('Hasil Konsolidasi'),
                'type': 'ir.actions.act_window',
                'res_model': 'legal.regulation',
                'res_id': new_regulation.id,
                'view_mode': 'form',
                'target': 'current',
                'context': {
                    'form_view_initial_mode': 'readonly',
                }
            }
        else:
            # Return action to open consolidation record
            return {
                'name': _('Hasil Konsolidasi'),
                'type': 'ir.actions.act_window',
                'res_model': 'legal.regulation.consolidation',
                'res_id': consolidation.id,
                'view_mode': 'form',
                'target': 'current',
            }

    def action_preview(self):
        """Preview hasil konsolidasi tanpa save"""
        self.ensure_one()
        
        if not self.regulation_ids:
            raise UserError(_('Pilih minimal satu peraturan untuk preview.'))
        
        # Create temporary consolidation (won't be saved to DB permanently)
        consolidation = self.env['legal.regulation.consolidation'].new({
            'name': self.name or 'Preview',
            'description': self.description,
            'regulation_ids': [(6, 0, self.regulation_ids.ids)],
            'display_mode': self.display_mode,
        })
        
        # Generate HTML
        sorted_regulations = self.regulation_ids.sorted(key=lambda r: (r.tahun, r.nomor))
        parsed_data = []
        for reg in sorted_regulations:
            structure = consolidation._parse_regulation_structure(reg)
            parsed_data.append({
                'regulation': reg,
                'structure': structure
            })
        
        if self.display_mode == 'annotated':
            html = consolidation._generate_annotated_html(parsed_data)
        elif self.display_mode == 'final':
            html = consolidation._generate_final_html(parsed_data)
        elif self.display_mode == 'history':
            html = consolidation._generate_history_html(parsed_data)
        else:
            html = consolidation._generate_comparison_html(parsed_data)
        
        # Return wizard with preview
        return {
            'name': _('Preview Konsolidasi'),
            'type': 'ir.actions.act_window',
            'res_model': 'consolidation.preview.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_html_preview': html,
                'default_parent_wizard_id': self.id,
            }
        }


class ConsolidationPreviewWizard(models.TransientModel):
    """Wizard untuk menampilkan preview HTML"""
    _name = 'consolidation.preview.wizard'
    _description = 'Preview Konsolidasi'

    html_preview = fields.Html(
        string='Preview',
        readonly=True
    )
    
    parent_wizard_id = fields.Many2one(
        'consolidation.wizard',
        string='Parent Wizard'
    )

    def action_back(self):
        """Kembali ke wizard utama"""
        self.ensure_one()
        
        if self.parent_wizard_id:
            return {
                'name': _('Konsolidasi Peraturan'),
                'type': 'ir.actions.act_window',
                'res_model': 'consolidation.wizard',
                'res_id': self.parent_wizard_id.id,
                'view_mode': 'form',
                'target': 'new',
            }
        
        return {'type': 'ir.actions.act_window_close'}

    def action_generate(self):
        """Generate konsolidasi (redirect ke wizard utama)"""
        self.ensure_one()
        
        if self.parent_wizard_id:
            return self.parent_wizard_id.action_generate_consolidation()
        
        return {'type': 'ir.actions.act_window_close'}
