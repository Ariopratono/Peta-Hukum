# -*- coding: utf-8 -*-
from odoo import models, fields, api

class LegalExpert(models.Model):
    _name = 'legal.expert'
    _description = 'Legal Expert'

    user_id = fields.Many2one('res.users', string='User', required=True, ondelete='cascade')
    name = fields.Char(string='Name', related='user_id.name', store=True, readonly=False)
    profile_picture = fields.Image(string='Profile Picture', related='user_id.image_1920', store=True, readonly=False)

    # Gelar dan Spesialisasi
    gelar = fields.Char(string='Gelar', help='Gelar lengkap, contoh: Prof. Dr., S.H., M.Hum.')
    specialization = fields.Char(string='Spesialisasi', help='Bidang keahlian, contoh: Filsafat Hukum, Penalaran Hukum')

    role = fields.Selection([
        ('lbh', 'LBH'),
        ('lawyer', 'Lawyer'),
        ('notary', 'Notary'),
        ('curator', 'Kurator Konsultan HKI'),
        # ('judge', 'Judge'),
        # ('prosecutor', 'Prosecutor'),
        # ('police', 'Police'),
        # ('other', 'Other Legal Expert'),
    ], string='Role', required=True, default='lawyer')

    experience = fields.Integer(string='Experience (Years)', default=0)
    ranking = fields.Float(string='Ranking', default=0.0)
    handled_client = fields.Integer(string='Handled Clients', default=0)
    availability = fields.Boolean(string='Availability', default=True)
    description = fields.Text(string='Description')

    # Informasi Kontak & Pendidikan
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    education = fields.Text(string='Education', help='Riwayat pendidikan')

    @api.depends('name', 'gelar')
    def _compute_display_name(self):
        for expert in self:
            if expert.gelar:
                expert.display_name = "%s %s" % (expert.name, expert.gelar)
            else:
                expert.display_name = expert.name or ''

    def name_get(self):
        result = []
        for expert in self:
            name = "%s (%s)" % (expert.name, dict(self._fields['role'].selection).get(expert.role))
            result.append((expert.id, name))
        return result
