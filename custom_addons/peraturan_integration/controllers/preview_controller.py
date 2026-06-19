from odoo import http
from odoo.http import request
from docx import Document
from io import BytesIO
import base64
import html

class RegulationPreviewController(http.Controller):
    @http.route('/regulations/preview/<int:reg_id>', type='http', auth="public", website=True)
    def regulation_preview(self, reg_id, **kwargs):
        """Menampilkan preview HTML dari dokumen konsolidasi yang terkait dengan legal.regulation"""
        regulation = request.env['legal.regulation'].sudo().browse(reg_id)
        if not regulation or not regulation.consolidation_id:
            return request.not_found()

        cons = regulation.consolidation_id
        if not cons.file:
            return request.not_found()

        try:
            file_bytes = base64.b64decode(cons.file)
            doc = Document(BytesIO(file_bytes))
        except Exception as e:
            return request.render('website.404', {
                'error': f"Gagal membuka dokumen konsolidasi: {str(e)}"
            })

        # Konversi isi docx ke HTML sederhana
        html_content = ["<div class='regulation-preview'>"]
        for p in doc.paragraphs:
            style = (p.style.name or '').lower()
            text = html.escape(p.text.strip())
            if not text:
                continue
            if 'heading' in style:
                html_content.append(f"<h4>{text}</h4>")
            else:
                html_content.append(f"<p>{text}</p>")
        html_content.append("</div>")
        html_body = "\n".join(html_content)

        return request.render("peraturan_integration_legal.regulation_preview_template", {
            "regulation": regulation,
            "html_body": html_body,
        })
