# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class SimpleRegulationTest(http.Controller):

    @http.route('/test/regulations', type='http', auth='public', website=True)
    def test_regulations(self, **kw):
        """Simple test untuk cek apakah model legal.regulation tersedia"""
        try:
            # Test access model
            if 'legal.regulation' not in request.env:
                return "<h1>Model legal.regulation tidak ditemukan!</h1><p>Module legal_regulations mungkin belum terinstall.</p>"
            
            # Test query
            count = request.env['legal.regulation'].sudo().search_count([])
            regulations = request.env['legal.regulation'].sudo().search([], limit=5)
            
            html = f"<h1>Test Legal Regulations</h1>"
            html += f"<p><strong>Total regulations:</strong> {count}</p>"
            html += "<h3>Sample data:</h3><ul>"
            
            for reg in regulations:
                html += f"<li>{reg.judul} - {reg.bentuk_singkat} No. {reg.nomor}/{reg.tahun}</li>"
            
            html += "</ul>"
            html += "<p><a href='/regulations'>Go to Regulations Page</a></p>"
            
            return html
            
        except Exception as e:
            return f"<h1>Error!</h1><p>{str(e)}</p>"