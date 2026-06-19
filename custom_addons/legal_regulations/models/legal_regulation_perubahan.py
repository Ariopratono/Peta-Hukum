# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import logging

_logger = logging.getLogger(__name__)


class LegalRegulationPerubahan(models.Model):
    """
    Model untuk melacak perubahan antar peraturan.
    Contoh: UU No. 11/2008 diubah oleh UU No. 19/2016 dan UU No. 1/2024
    """
    _name = 'legal.regulation.perubahan'
    _description = 'Perubahan Peraturan Hukum'
    _order = 'tanggal_perubahan, sequence'
    
    name = fields.Char(
        string='Nama',
        compute='_compute_name',
        store=True
    )
    
    # Peraturan induk (yang diubah)
    peraturan_induk_id = fields.Many2one(
        'legal.regulation',
        string='Peraturan Induk',
        required=True,
        ondelete='cascade',
        help='UU/Peraturan yang diubah'
    )
    
    # Peraturan pengubah
    peraturan_pengubah_id = fields.Many2one(
        'legal.regulation',
        string='Diubah Oleh',
        ondelete='cascade',
        help='UU/Peraturan yang mengubah (opsional - bisa pilih yang sudah ada atau upload file langsung)'
    )
    
    # Upload file TXT perubahan langsung (tanpa harus bikin record peraturan dulu)
    file_txt_perubahan = fields.Binary(
        string='File TXT Perubahan',
        attachment=True,
        help='Upload file TXT perubahan di sini. Jika diisi, file ini yang akan dipakai untuk konsolidasi'
    )
    
    file_txt_perubahan_name = fields.Char(
        string='Nama File',
        help='Nama file perubahan'
    )
    
    # Info perubahan
    nama_perubahan = fields.Char(
        string='Nama Perubahan',
        help='Contoh: UU No. 19/2016, UU No. 1/2024, dsb'
    )
    
    tahun_perubahan = fields.Integer(
        string='Tahun',
        help='Tahun perubahan'
    )
    
    tanggal_perubahan = fields.Date(
        string='Tanggal Perubahan',
        help='Tanggal penetapan perubahan'
    )
    
    sequence = fields.Integer(
        string='Urutan',
        default=10,
        help='Urutan perubahan (untuk sorting)'
    )
    
    keterangan = fields.Text(
        string='Keterangan',
        help='Catatan tambahan tentang perubahan ini'
    )
    
    @api.depends('peraturan_induk_id', 'peraturan_pengubah_id', 'nama_perubahan')
    def _compute_name(self):
        for record in self:
            if record.peraturan_pengubah_id:
                # Jika pakai relasi ke peraturan yang sudah ada
                if record.peraturan_induk_id:
                    record.name = f"{record.peraturan_pengubah_id.nama_lengkap} mengubah {record.peraturan_induk_id.nama_lengkap}"
                else:
                    record.name = record.peraturan_pengubah_id.nama_lengkap
            elif record.nama_perubahan:
                # Jika upload manual
                if record.peraturan_induk_id:
                    record.name = f"{record.nama_perubahan} mengubah {record.peraturan_induk_id.nama_lengkap}"
                else:
                    record.name = record.nama_perubahan
            else:
                record.name = 'Perubahan Baru'
