# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
import re
from difflib import SequenceMatcher
import logging

_logger = logging.getLogger(__name__)


class LegalRegulationConsolidation(models.Model):
    """
    Model untuk menyimpan hasil konsolidasi/penggabungan beberapa versi peraturan.
    Menampilkan versi gabungan dengan tracking perubahan per pasal.
    """
    _name = 'legal.regulation.consolidation'
    _description = 'Konsolidasi Peraturan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    name = fields.Char(
        string='Nama Konsolidasi',
        required=True,
        help='Nama hasil konsolidasi, misal: UU ITE Terpadu (2008-2016-2024)'
    )
    
    description = fields.Text(
        string='Deskripsi',
        help='Deskripsi singkat tentang konsolidasi ini'
    )
    
    # Pilih peraturan yang akan digabung (UU Induk + UU Perubahannya)
    regulation_ids = fields.Many2many(
        'legal.regulation',
        'consolidation_regulation_rel',
        'consolidation_id',
        'regulation_id',
        string='Peraturan yang Digabung',
        required=True,
        help='Pilih UU Induk dan semua UU perubahannya (urutan: dari yang paling lama ke paling baru)'
    )
    
    # Mode tampilan
    display_mode = fields.Selection([
        ('annotated', 'Mode Anotasi (Tampilkan Perubahan)'),
        ('final', 'Mode Final (Versi Terbaru Saja)'),
        ('history', 'Mode Riwayat (Semua Versi)'),
        ('comparison', 'Mode Perbandingan (Side by Side)')
    ], string='Mode Tampilan', default='annotated', required=True)
    
    # Hasil konsolidasi dalam HTML
    consolidated_html = fields.Html(
        string='Hasil Konsolidasi',
        help='Hasil penggabungan dalam format HTML dengan highlight perubahan'
    )
    
    # Statistik perubahan
    total_articles = fields.Integer(
        string='Total Pasal',
        compute='_compute_statistics',
        store=True
    )
    
    articles_added = fields.Integer(
        string='Pasal Ditambah',
        compute='_compute_statistics',
        store=True
    )
    
    articles_modified = fields.Integer(
        string='Pasal Diubah',
        compute='_compute_statistics',
        store=True
    )
    
    articles_deleted = fields.Integer(
        string='Pasal Dihapus',
        compute='_compute_statistics',
        store=True
    )
    
    # Metadata
    created_date = fields.Datetime(
        string='Tanggal Dibuat',
        default=fields.Datetime.now,
        readonly=True
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('generated', 'Sudah Digenerate'),
        ('published', 'Dipublikasikan')
    ], string='Status', default='draft')

    @api.depends('regulation_ids', 'consolidated_html')
    def _compute_statistics(self):
        """Hitung statistik perubahan dari hasil konsolidasi"""
        for record in self:
            if not record.consolidated_html:
                record.total_articles = 0
                record.articles_added = 0
                record.articles_modified = 0
                record.articles_deleted = 0
                continue
                
            html = record.consolidated_html
            # Count dari tag HTML yang kita buat
            record.total_articles = html.count('class="pasal-header"')
            record.articles_added = html.count('class="article-added"')
            record.articles_modified = html.count('class="article-modified"')
            record.articles_deleted = html.count('class="article-deleted"')

    def action_generate_consolidation(self):
        """Generate hasil konsolidasi dari peraturan yang dipilih"""
        self.ensure_one()
        
        if not self.regulation_ids:
            raise UserError(_('Pilih minimal satu peraturan untuk digabung.'))
        
        if len(self.regulation_ids) < 2:
            raise UserError(_('Pilih minimal dua peraturan (UU Induk + UU Perubahan) untuk konsolidasi.'))
        
        # Urutkan berdasarkan tahun (dari lama ke baru)
        sorted_regulations = self.regulation_ids.sorted(key=lambda r: (r.tahun, r.nomor))
        
        _logger.info(f"Generating consolidation for {len(sorted_regulations)} regulations...")
        
        try:
            # Parse struktur pasal dari setiap peraturan
            parsed_data = []
            for reg in sorted_regulations:
                structure = self._parse_regulation_structure(reg)
                parsed_data.append({
                    'regulation': reg,
                    'structure': structure
                })
            
            # Generate HTML berdasarkan mode
            if self.display_mode == 'annotated':
                html = self._generate_annotated_html(parsed_data)
            elif self.display_mode == 'final':
                html = self._generate_final_html(parsed_data)
            elif self.display_mode == 'history':
                html = self._generate_history_html(parsed_data)
            else:  # comparison
                html = self._generate_comparison_html(parsed_data)
            
            self.consolidated_html = html
            self.state = 'generated'
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sukses'),
                    'message': _('Konsolidasi berhasil digenerate!'),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            _logger.error(f"Error generating consolidation: {str(e)}", exc_info=True)
            raise UserError(_('Error saat generate konsolidasi: %s') % str(e))

    def _parse_regulation_structure(self, regulation):
        """
        Parse struktur pasal dari isi_peraturan HTML
        Returns: dict dengan key = nomor pasal, value = {'title': '', 'content': '', 'ayat': []}
        """
        structure = {}
        
        if not regulation.isi_peraturan:
            return structure
        
        html = regulation.isi_peraturan
        
        # Extract pasal menggunakan regex dari HTML
        # Pattern untuk mendeteksi Pasal
        pasal_pattern = re.compile(
            r'<h[23][^>]*pasal-header[^>]*>.*?Pasal\s+(\d+).*?</h[23]>(.*?)(?=<h[23][^>]*pasal-header|<div[^>]*class="penjelasan|$)',
            re.DOTALL | re.IGNORECASE
        )
        
        for match in pasal_pattern.finditer(html):
            pasal_no = match.group(1)
            content = match.group(2)
            
            # Clean HTML tags untuk comparison
            clean_content = re.sub(r'<[^>]+>', ' ', content)
            clean_content = re.sub(r'\s+', ' ', clean_content).strip()
            
            # Extract ayat jika ada
            ayat_list = []
            ayat_pattern = re.compile(r'\((\d+)\)\s*([^(]+?)(?=\(\d+\)|$)', re.DOTALL)
            for ayat_match in ayat_pattern.finditer(clean_content):
                ayat_no = ayat_match.group(1)
                ayat_text = ayat_match.group(2).strip()
                ayat_list.append({
                    'number': ayat_no,
                    'text': ayat_text
                })
            
            structure[pasal_no] = {
                'number': pasal_no,
                'content': content,
                'clean_content': clean_content,
                'ayat': ayat_list
            }
        
        _logger.info(f"Parsed {len(structure)} pasal from {regulation.nama_lengkap}")
        return structure

    def _generate_annotated_html(self, parsed_data):
        """
        Generate HTML dengan anotasi perubahan.
        Menampilkan versi terbaru dengan catatan apa yang berubah.
        """
        html_parts = []
        
        # Header
        reg_names = ', '.join([d['regulation'].nama_lengkap for d in parsed_data])
        html_parts.append(f"""
        <div class="consolidated-document">
            <style>
                .consolidated-header {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }}
                .pasal-header {{
                    background: #007bff;
                    color: white;
                    padding: 10px 15px;
                    margin-top: 20px;
                    border-radius: 5px;
                    font-weight: bold;
                }}
                .article-unchanged {{
                    border-left: 4px solid #28a745;
                    padding-left: 15px;
                    margin: 10px 0;
                }}
                .article-modified {{
                    border-left: 4px solid #ffc107;
                    padding-left: 15px;
                    margin: 10px 0;
                    background: #fff3cd;
                }}
                .article-added {{
                    border-left: 4px solid #17a2b8;
                    padding-left: 15px;
                    margin: 10px 0;
                    background: #d1ecf1;
                }}
                .article-deleted {{
                    border-left: 4px solid #dc3545;
                    padding-left: 15px;
                    margin: 10px 0;
                    background: #f8d7da;
                    text-decoration: line-through;
                    opacity: 0.7;
                }}
                .change-note {{
                    background: #fff3cd;
                    border-left: 3px solid #ffc107;
                    padding: 10px;
                    margin: 10px 0;
                    font-style: italic;
                    font-size: 0.9em;
                }}
                .version-badge {{
                    display: inline-block;
                    padding: 3px 8px;
                    border-radius: 3px;
                    font-size: 0.85em;
                    margin-right: 5px;
                }}
                .badge-original {{
                    background: #28a745;
                    color: white;
                }}
                .badge-amended {{
                    background: #ffc107;
                    color: #000;
                }}
                .badge-current {{
                    background: #007bff;
                    color: white;
                }}
            </style>
            
            <div class="consolidated-header">
                <h1>📋 Naskah Konsolidasi: {self.name}</h1>
                <p><strong>Mode:</strong> Anotasi (Menampilkan Perubahan)</p>
                <p><strong>Peraturan yang Digabung:</strong> {reg_names}</p>
                <p><strong>Tanggal Generate:</strong> {fields.Datetime.now().strftime('%d %B %Y %H:%M')}</p>
            </div>
        """)
        
        # Collect all unique pasal numbers across all versions
        all_pasal_numbers = set()
        for data in parsed_data:
            all_pasal_numbers.update(data['structure'].keys())
        
        # Sort pasal numbers numerically
        sorted_pasal_numbers = sorted(all_pasal_numbers, key=lambda x: int(x))
        
        # Process each pasal
        for pasal_no in sorted_pasal_numbers:
            html_parts.append(f'<div class="pasal-container">')
            html_parts.append(f'<h2 class="pasal-header">Pasal {pasal_no}</h2>')
            
            # Collect versions of this pasal
            versions = []
            for idx, data in enumerate(parsed_data):
                reg = data['regulation']
                structure = data['structure']
                
                if pasal_no in structure:
                    versions.append({
                        'index': idx,
                        'regulation': reg,
                        'data': structure[pasal_no]
                    })
            
            if not versions:
                continue
            
            # Determine status
            if len(versions) == 1 and versions[0]['index'] == 0:
                # Pasal hanya ada di versi pertama (deleted in later versions)
                status_class = 'article-deleted'
                status_text = '❌ Dihapus pada versi selanjutnya'
            elif len(versions) == 1 and versions[0]['index'] > 0:
                # Pasal ditambah di versi later
                status_class = 'article-added'
                status_text = f'✅ Ditambahkan oleh {versions[0]["regulation"].nama_lengkap}'
            elif len(versions) > 1:
                # Check if content changed
                first_content = versions[0]['data']['clean_content']
                last_content = versions[-1]['data']['clean_content']
                similarity = SequenceMatcher(None, first_content, last_content).ratio()
                
                if similarity < 0.95:
                    status_class = 'article-modified'
                    status_text = f'⚠️ Diubah oleh {versions[-1]["regulation"].nama_lengkap}'
                else:
                    status_class = 'article-unchanged'
                    status_text = '✓ Tidak berubah'
            else:
                status_class = 'article-unchanged'
                status_text = '✓ Tidak berubah'
            
            # Display latest version content
            latest = versions[-1]
            html_parts.append(f'<div class="{status_class}">')
            html_parts.append(f'<div class="change-note"><strong>{status_text}</strong></div>')
            html_parts.append(latest['data']['content'])
            
            # Show change history if modified
            if len(versions) > 1 and status_class == 'article-modified':
                html_parts.append('<div class="change-note">')
                html_parts.append('<strong>📜 Riwayat Perubahan:</strong><ul>')
                for v in versions:
                    badge_class = 'badge-original' if v['index'] == 0 else ('badge-current' if v == versions[-1] else 'badge-amended')
                    html_parts.append(f'<li><span class="version-badge {badge_class}">{v["regulation"].nama_lengkap}</span></li>')
                html_parts.append('</ul></div>')
            
            html_parts.append('</div>')  # Close status div
            html_parts.append('</div>')  # Close pasal-container
        
        html_parts.append('</div>')  # Close consolidated-document
        
        return '\n'.join(html_parts)

    def _generate_final_html(self, parsed_data):
        """Generate HTML versi final (terbaru saja, tanpa anotasi)"""
        html_parts = []
        
        latest_reg = parsed_data[-1]['regulation']
        latest_structure = parsed_data[-1]['structure']
        
        html_parts.append(f"""
        <div class="consolidated-document">
            <div class="consolidated-header">
                <h1>📄 Naskah Final: {self.name}</h1>
                <p><strong>Versi Terbaru:</strong> {latest_reg.nama_lengkap}</p>
                <p><strong>Tanggal Generate:</strong> {fields.Datetime.now().strftime('%d %B %Y %H:%M')}</p>
            </div>
        """)
        
        # Sort and display all pasal from latest version
        sorted_pasal = sorted(latest_structure.keys(), key=lambda x: int(x))
        
        for pasal_no in sorted_pasal:
            data = latest_structure[pasal_no]
            html_parts.append(f'<h2 class="pasal-header">Pasal {pasal_no}</h2>')
            html_parts.append(f'<div class="article-unchanged">{data["content"]}</div>')
        
        html_parts.append('</div>')
        
        return '\n'.join(html_parts)

    def _generate_history_html(self, parsed_data):
        """Generate HTML dengan semua versi ditampilkan per pasal"""
        html_parts = []
        
        reg_names = ', '.join([d['regulation'].nama_lengkap for d in parsed_data])
        html_parts.append(f"""
        <div class="consolidated-document">
            <div class="consolidated-header">
                <h1>📚 Riwayat Lengkap: {self.name}</h1>
                <p><strong>Semua Versi:</strong> {reg_names}</p>
                <p><strong>Tanggal Generate:</strong> {fields.Datetime.now().strftime('%d %B %Y %H:%M')}</p>
            </div>
        """)
        
        # Collect all pasal numbers
        all_pasal_numbers = set()
        for data in parsed_data:
            all_pasal_numbers.update(data['structure'].keys())
        
        sorted_pasal_numbers = sorted(all_pasal_numbers, key=lambda x: int(x))
        
        for pasal_no in sorted_pasal_numbers:
            html_parts.append(f'<h2 class="pasal-header">Pasal {pasal_no}</h2>')
            
            # Show each version
            for idx, data in enumerate(parsed_data):
                reg = data['regulation']
                structure = data['structure']
                
                if pasal_no in structure:
                    badge_class = 'badge-original' if idx == 0 else ('badge-current' if idx == len(parsed_data)-1 else 'badge-amended')
                    html_parts.append(f'<div class="article-unchanged">')
                    html_parts.append(f'<span class="version-badge {badge_class}">{reg.nama_lengkap}</span>')
                    html_parts.append(structure[pasal_no]['content'])
                    html_parts.append('</div>')
                else:
                    html_parts.append(f'<div class="article-deleted">')
                    html_parts.append(f'<span class="version-badge badge-original">{reg.nama_lengkap}</span>')
                    html_parts.append(f'<p><em>[Pasal ini tidak ada di versi ini]</em></p>')
                    html_parts.append('</div>')
        
        html_parts.append('</div>')
        
        return '\n'.join(html_parts)

    def _generate_comparison_html(self, parsed_data):
        """Generate HTML side-by-side comparison"""
        html_parts = []
        
        html_parts.append(f"""
        <div class="consolidated-document">
            <style>
                .comparison-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                .comparison-table th {{
                    background: #007bff;
                    color: white;
                    padding: 10px;
                    border: 1px solid #ddd;
                }}
                .comparison-table td {{
                    padding: 10px;
                    border: 1px solid #ddd;
                    vertical-align: top;
                }}
                .comparison-table tr:nth-child(even) {{
                    background: #f8f9fa;
                }}
            </style>
            <div class="consolidated-header">
                <h1>🔍 Perbandingan: {self.name}</h1>
                <p><strong>Tanggal Generate:</strong> {fields.Datetime.now().strftime('%d %B %Y %H:%M')}</p>
            </div>
        """)
        
        # Create table header
        html_parts.append('<table class="comparison-table">')
        html_parts.append('<thead><tr>')
        html_parts.append('<th>Pasal</th>')
        for data in parsed_data:
            html_parts.append(f'<th>{data["regulation"].nama_lengkap}</th>')
        html_parts.append('</tr></thead><tbody>')
        
        # Collect all pasal numbers
        all_pasal_numbers = set()
        for data in parsed_data:
            all_pasal_numbers.update(data['structure'].keys())
        
        sorted_pasal_numbers = sorted(all_pasal_numbers, key=lambda x: int(x))
        
        # Create rows
        for pasal_no in sorted_pasal_numbers:
            html_parts.append('<tr>')
            html_parts.append(f'<td><strong>Pasal {pasal_no}</strong></td>')
            
            for data in parsed_data:
                structure = data['structure']
                if pasal_no in structure:
                    html_parts.append(f'<td>{structure[pasal_no]["content"]}</td>')
                else:
                    html_parts.append('<td><em>[Tidak ada]</em></td>')
            
            html_parts.append('</tr>')
        
        html_parts.append('</tbody></table>')
        html_parts.append('</div>')
        
        return '\n'.join(html_parts)

    def action_publish(self):
        """Publish konsolidasi (ubah state menjadi published)"""
        self.ensure_one()
        if self.state != 'generated':
            raise UserError(_('Generate konsolidasi terlebih dahulu sebelum publish.'))
        
        self.state = 'published'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Sukses'),
                'message': _('Konsolidasi berhasil dipublikasikan!'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_back_to_draft(self):
        """Kembalikan ke draft untuk edit"""
        self.ensure_one()
        self.state = 'draft'
