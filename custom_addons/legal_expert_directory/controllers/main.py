# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class LegalExpertDirectory(http.Controller):

    @http.route(['/legal/experts', '/legal/experts/page/<int:page>'], type='http', auth="public", website=True)
    def experts_directory(self, page=1, **kw):
        domain = []
        if kw.get('role'):
            domain.append(('role', '=', kw.get('role')))

        LegalExpert = request.env['legal.expert'].sudo()
        experts = LegalExpert.search(domain)

        roles = dict(LegalExpert._fields['role'].selection)

        values = {
            'experts': experts,
            'roles': roles,
            'current_role': kw.get('role', ''),
        }
        return request.render('legal_expert_directory.website_expert_directory', values)

    @http.route('/legal/expert/<int:expert_id>', type='http', auth="public", website=True)
    def expert_detail(self, expert_id, **kw):
        """Halaman detail legal expert"""
        expert = request.env['legal.expert'].sudo().browse(expert_id)

        if not expert.exists():
            return request.not_found()

        # Get other experts for "related" section
        other_experts = request.env['legal.expert'].sudo().search([
            ('id', '!=', expert_id),
            ('role', '=', expert.role),
        ], limit=5)

        roles = dict(request.env['legal.expert']._fields['role'].selection)

        values = {
            'expert': expert,
            'other_experts': other_experts,
            'roles': roles,
            'role_label': roles.get(expert.role, ''),
        }
        return request.render('legal_expert_directory.website_expert_detail', values)
