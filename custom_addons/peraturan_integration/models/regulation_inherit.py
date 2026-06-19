from odoo import models, fields, api

class LegalRegulation(models.Model):
    _inherit = "legal.regulation"

    consolidation_id = fields.Many2one(
        "peraturan.consolidation",
        string="Konsolidasi Peraturan",
        ondelete="set null",
        help="Tautan ke dokumen hasil konsolidasi dari modul Peraturan Merger.",
    )

    has_consolidation = fields.Boolean(
        compute="_compute_has_consolidation", store=False, string="Punya Konsolidasi"
    )

    @api.depends("consolidation_id")
    def _compute_has_consolidation(self):
        for rec in self:
            rec.has_consolidation = bool(rec.consolidation_id)

    # helper untuk membuat link unduhan
    def get_consolidation_download_url(self):
        self.ensure_one()
        if self.consolidation_id and self.consolidation_id.file and self.consolidation_id.file_name:
            return f"/web/content/peraturan.consolidation/{self.consolidation_id.id}/file/{self.consolidation_id.file_name}?download=true"
        return False

class PeraturanConsolidation(models.Model):
    _inherit = "peraturan.consolidation"

    def _sync_to_legal_regulation(self):
        """
        Sinkronisasi otomatis: cari legal.regulation berdasarkan nomor/tahun peraturan
        dan tautkan consolidation_id.
        """
        for rec in self:
            rule = rec.rule_id
            if not rule:
                continue
            nomor = (rule.nomor or "").strip()
            tahun = (rule.tahun or "").strip()
            if not nomor and not tahun:
                continue

            legal = self.env["legal.regulation"].search([
                ("name", "ilike", nomor),
                ("year", "=", tahun),
            ], limit=1)

            if legal:
                legal.consolidation_id = rec
        return True
