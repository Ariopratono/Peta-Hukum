from odoo import models, fields, api

class LegalVerdict(models.Model):
    _name = 'legal.verdict'
    _description = 'Indonesia Legal Verdict Data'
    _order = 'tanggal_putusan desc, name'

    name = fields.Char(string='Nomor Putusan', required=True)
    institution = fields.Selection([
        ('mk', 'Mahkamah Konstitusi (MK)'),
        ('ma', 'Mahkamah Agung (MA)')
    ], string='Lembaga', required=True)

    judul = fields.Char(string='Judul/Perkara', required=True)
    tanggal_putusan = fields.Date(string='Tanggal Putusan')
    status = fields.Char(string='Status')

    link_url = fields.Char(string='Link Sumber')
    file_url = fields.Char(string='Link File PDF')

    deskripsi = fields.Text(string='Deskripsi/Amar Putusan')

    kategori = fields.Char(string='Kategori/Klasifikasi')

    verdict_text = fields.Text(string='Teks Putusan')
    txt_file = fields.Binary(string='File Teks (.txt)', attachment=True)
    txt_filename = fields.Char(string='Nama File Teks')

    active = fields.Boolean(default=True)
