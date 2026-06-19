# peraturan_merger/models/peraturan.py
from odoo import models, fields, api, _
import hashlib
import base64
from datetime import datetime
from .parser import DocParser, merge_versions_to_consolidation

class PeraturanRule(models.Model):
    _name = "peraturan.rule"
    _description = "Peraturan (Master)"

    name = fields.Char(string="Nama / Judul", required=True)
    nomor = fields.Char(string="Nomor")
    tahun = fields.Char(string="Tahun")
    description = fields.Text(string="Deskripsi")
    version_ids = fields.One2many('peraturan.version', 'rule_id', string='Versi')

class PeraturanVersion(models.Model):
    _name = "peraturan.version"
    _description = "Versi Peraturan"

    rule_id = fields.Many2one('peraturan.rule', string='Peraturan', required=True, ondelete='cascade')
    name = fields.Char(string='Label / Nama Versi', required=True)
    sumber = fields.Char(string='Sumber (URL / Catatan)')
    tanggal = fields.Date(string='Tanggal Sumber')
    file = fields.Binary(string='File (PDF/DOCX)', attachment=True)
    file_name = fields.Char(string='Nama File')
    checksum = fields.Char(string='Checksum')
    article_ids = fields.One2many('peraturan.article', 'version_id', string='Pasal')

    @api.model
    def create_from_bytes(self, rule_id, filebytes, filename, sumber=None, tanggal=None):
        """
        Helper to create a PeraturanVersion from raw bytes (not base64).
        """
        checksum = hashlib.sha256(filebytes).hexdigest()
        existing = self.search([('checksum', '=', checksum), ('rule_id', '=', rule_id)], limit=1)
        if existing:
            return existing

        vals = {
            'rule_id': rule_id,
            'name': filename,
            'sumber': sumber or '',
            'file': base64.b64encode(filebytes),
            'file_name': filename,
            'checksum': checksum,
        }
        if tanggal:
            vals['tanggal'] = tanggal
        ver = self.create(vals)

        # parse and populate structured content
        parser = DocParser()
        try:
            structure = parser.parse_bytes(filebytes, filename)
        except Exception:
            structure = parser.parse_text_fallback(filebytes.decode('utf-8', errors='ignore'))
        # structure: list of dicts {article_no, article_title, paragraphs: [{label,text,order}]}
        for a in structure:
            art = self.env['peraturan.article'].create({
                'version_id': ver.id,
                'number': a.get('article_no'),
                'title': a.get('article_title') or '',
            })
            for p in a.get('paragraphs', []):
                self.env['peraturan.paragraph'].create({
                    'article_id': art.id,
                    'label': p.get('label') or '',
                    'text': p.get('text') or '',
                    'sequence': p.get('order') or 0,
                })
        return ver

class PeraturanArticle(models.Model):
    _name = "peraturan.article"
    _description = "Pasal per Versi"

    version_id = fields.Many2one('peraturan.version', string='Versi', ondelete='cascade')
    number = fields.Char(string='Nomor Pasal')
    title = fields.Char(string='Judul Pasal')
    paragraph_ids = fields.One2many('peraturan.paragraph', 'article_id', string='Ayat / Anak Pasal')

class PeraturanParagraph(models.Model):
    _name = "peraturan.paragraph"
    _description = "Ayat/Anak Pasal"

    article_id = fields.Many2one('peraturan.article', string='Pasal', ondelete='cascade')
    label = fields.Char(string='Label (ayat / huruf)')
    text = fields.Text(string='Teks')
    sequence = fields.Integer(string='Sequence', default=0)

class PeraturanConsolidation(models.Model):
    _name = "peraturan.consolidation"
    _description = "Hasil Konsolidasi Peraturan"

    name = fields.Char(string='Nama', required=True)
    rule_id = fields.Many2one('peraturan.rule', string='Peraturan', required=True)
    version_ids = fields.Many2many('peraturan.version', string='Versi')
    created_on = fields.Datetime(string='Dibuat Pada', default=lambda self: fields.Datetime.now())
    file = fields.Binary(string='Hasil DOCX', attachment=True)
    file_name = fields.Char(string='Nama File')

    def action_generate(self, mode='annotated'):
        versions = self.version_ids.sorted(key=lambda r: r.tanggal or r.create_date)
        doc_bytes = merge_versions_to_consolidation(self, versions, mode=mode)
        # store as base64 (string)
        self.file = base64.b64encode(doc_bytes)
        self.file_name = f"{self.rule_id.name.replace(' ', '_')}_consolidated.docx"
        return True
