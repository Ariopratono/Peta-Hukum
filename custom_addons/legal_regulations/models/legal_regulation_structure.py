# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class LegalRegulationPasal(models.Model):
    """Model untuk menyimpan struktur Pasal dari peraturan"""
    _name = 'legal.regulation.pasal'
    _description = 'Pasal Peraturan Hukum'
    _order = 'sequence, nomor_pasal'
    _rec_name = 'display_name'
    
    # Relasi ke peraturan induk
    regulation_id = fields.Many2one(
        'legal.regulation', 
        string='Peraturan',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    # Informasi Pasal
    nomor_pasal = fields.Char(
        'Nomor Pasal', 
        required=True,
        help='Contoh: 1, 2, 3, 1A, dst'
    )
    
    judul_pasal = fields.Char(
        'Judul/Tema Pasal',
        help='Optional: judul atau tema pasal jika ada'
    )
    
    bab = fields.Char(
        'BAB',
        help='BAB tempat pasal ini berada (contoh: BAB I, BAB II)'
    )
    
    sequence = fields.Integer(
        'Urutan',
        default=10,
        help='Urutan pasal dalam peraturan'
    )
    
    # Isi pasal (jika tidak ada ayat, langsung isi di sini)
    isi_pasal = fields.Html(
        'Isi Pasal',
        help='Isi lengkap pasal jika tidak dibagi dalam ayat'
    )
    
    # Relasi ke ayat
    ayat_ids = fields.One2many(
        'legal.regulation.ayat',
        'pasal_id',
        string='Ayat-ayat',
        copy=True
    )
    
    ayat_count = fields.Integer(
        'Jumlah Ayat',
        compute='_compute_ayat_count',
        store=True
    )
    
    # Computed field untuk display
    display_name = fields.Char(
        'Display Name',
        compute='_compute_display_name',
        store=True
    )
    
    @api.depends('nomor_pasal', 'judul_pasal')
    def _compute_display_name(self):
        for record in self:
            if record.judul_pasal:
                record.display_name = f"Pasal {record.nomor_pasal} - {record.judul_pasal}"
            else:
                record.display_name = f"Pasal {record.nomor_pasal}"
    
    @api.depends('ayat_ids')
    def _compute_ayat_count(self):
        for record in self:
            record.ayat_count = len(record.ayat_ids)
    
    def action_view_ayat(self):
        """Action untuk melihat ayat-ayat dalam pasal ini"""
        self.ensure_one()
        return {
            'name': f'Ayat - {self.display_name}',
            'type': 'ir.actions.act_window',
            'res_model': 'legal.regulation.ayat',
            'view_mode': 'tree,form',
            'domain': [('pasal_id', '=', self.id)],
            'context': {'default_pasal_id': self.id}
        }


class LegalRegulationAyat(models.Model):
    """Model untuk menyimpan Ayat dari setiap Pasal"""
    _name = 'legal.regulation.ayat'
    _description = 'Ayat Pasal Peraturan Hukum'
    _order = 'sequence, nomor_ayat'
    _rec_name = 'display_name'
    
    # Relasi ke pasal induk
    pasal_id = fields.Many2one(
        'legal.regulation.pasal',
        string='Pasal',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    regulation_id = fields.Many2one(
        'legal.regulation',
        string='Peraturan',
        related='pasal_id.regulation_id',
        store=True,
        index=True
    )
    
    # Informasi Ayat
    nomor_ayat = fields.Char(
        'Nomor Ayat',
        required=True,
        help='Contoh: (1), (2), (3), dst'
    )
    
    sequence = fields.Integer(
        'Urutan',
        default=10,
        help='Urutan ayat dalam pasal'
    )
    
    # Isi ayat
    isi_ayat = fields.Html(
        'Isi Ayat',
        required=True,
        help='Isi lengkap ayat beserta penjelasannya'
    )
    
    # Relasi ke huruf/poin (jika ada sub-bagian)
    huruf_ids = fields.One2many(
        'legal.regulation.huruf',
        'ayat_id',
        string='Huruf/Poin',
        copy=True
    )
    
    huruf_count = fields.Integer(
        'Jumlah Huruf/Poin',
        compute='_compute_huruf_count',
        store=True
    )
    
    # Computed field untuk display
    display_name = fields.Char(
        'Display Name',
        compute='_compute_display_name',
        store=True
    )
    
    @api.depends('pasal_id.nomor_pasal', 'nomor_ayat')
    def _compute_display_name(self):
        for record in self:
            if record.pasal_id:
                record.display_name = f"Pasal {record.pasal_id.nomor_pasal} Ayat {record.nomor_ayat}"
            else:
                record.display_name = f"Ayat {record.nomor_ayat}"
    
    @api.depends('huruf_ids')
    def _compute_huruf_count(self):
        for record in self:
            record.huruf_count = len(record.huruf_ids)
    
    def action_view_huruf(self):
        """Action untuk melihat huruf/poin dalam ayat ini"""
        self.ensure_one()
        return {
            'name': f'Huruf/Poin - {self.display_name}',
            'type': 'ir.actions.act_window',
            'res_model': 'legal.regulation.huruf',
            'view_mode': 'tree,form',
            'domain': [('ayat_id', '=', self.id)],
            'context': {'default_ayat_id': self.id}
        }


class LegalRegulationHuruf(models.Model):
    """Model untuk menyimpan Huruf/Poin dari setiap Ayat"""
    _name = 'legal.regulation.huruf'
    _description = 'Huruf/Poin Ayat Peraturan Hukum'
    _order = 'sequence, huruf'
    _rec_name = 'display_name'
    
    # Relasi ke ayat induk
    ayat_id = fields.Many2one(
        'legal.regulation.ayat',
        string='Ayat',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    pasal_id = fields.Many2one(
        'legal.regulation.pasal',
        string='Pasal',
        related='ayat_id.pasal_id',
        store=True,
        index=True
    )
    
    regulation_id = fields.Many2one(
        'legal.regulation',
        string='Peraturan',
        related='ayat_id.regulation_id',
        store=True,
        index=True
    )
    
    # Informasi Huruf/Poin
    huruf = fields.Char(
        'Huruf/Nomor',
        required=True,
        help='Contoh: a, b, c atau 1, 2, 3'
    )
    
    sequence = fields.Integer(
        'Urutan',
        default=10,
        help='Urutan huruf/poin dalam ayat'
    )
    
    # Isi huruf/poin
    isi = fields.Html(
        'Isi',
        required=True,
        help='Isi lengkap huruf/poin'
    )
    
    # Computed field untuk display
    display_name = fields.Char(
        'Display Name',
        compute='_compute_display_name',
        store=True
    )
    
    @api.depends('pasal_id.nomor_pasal', 'ayat_id.nomor_ayat', 'huruf')
    def _compute_display_name(self):
        for record in self:
            if record.ayat_id and record.pasal_id:
                record.display_name = f"Pasal {record.pasal_id.nomor_pasal} Ayat {record.ayat_id.nomor_ayat} huruf {record.huruf}"
            elif record.ayat_id:
                record.display_name = f"Ayat {record.ayat_id.nomor_ayat} huruf {record.huruf}"
            else:
                record.display_name = f"Huruf {record.huruf}"
