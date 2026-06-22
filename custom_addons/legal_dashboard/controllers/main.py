# -*- coding: utf-8 -*-
from odoo.addons.web.controllers.view import View
from odoo.http import route, request

class LegalDashboardView(View):
    
    @route('/web/view/edit_custom', type='jsonrpc', auth="user")
    def edit_custom(self, custom_id=None, arch=None):
        """
        Override edit_custom to gracefully handle the case where a pre-filled 
        board view does not have a custom_id yet.
        """
        if not custom_id:
            # If there's no custom_id, we just return success without saving
            # to prevent the RPC TypeError when interacting with standard boards.
            return {'result': True}
        
        return super().edit_custom(custom_id, arch)
