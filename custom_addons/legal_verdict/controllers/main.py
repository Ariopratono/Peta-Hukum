from odoo import http
from odoo.http import request

class LegalVerdictController(http.Controller):

    @http.route(['/verdicts', '/verdicts/page/<int:page>'], type='http', auth="public", website=True)
    def verdicts(self, page=1, search='', institution='', **kw):
        domain = []
        if search:
            domain += ['|', ('name', 'ilike', search), ('judul', 'ilike', search)]
        if institution:
            domain += [('institution', '=', institution)]

        # Pagination logic
        limit = 10
        offset = (page - 1) * limit

        Verdict = request.env['legal.verdict'].sudo()
        total = Verdict.search_count(domain)
        verdicts = Verdict.search(domain, limit=limit, offset=offset)

        pager = request.website.pager(
            url='/verdicts',
            url_args={'search': search, 'institution': institution},
            total=total,
            page=page,
            step=limit
        )

        values = {
            'verdicts': verdicts,
            'pager': pager,
            'search': search,
            'institution': institution,
        }
        return request.render("legal_verdict.verdicts_page", values)

    @http.route(['/verdict/<model("legal.verdict"):verdict>'], type='http', auth="public", website=True)
    def verdict_detail(self, verdict, **kw):
        values = {
            'verdict': verdict,
        }
        return request.render("legal_verdict.verdict_detail_page", values)
