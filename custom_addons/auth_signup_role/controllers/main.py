import base64
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.http import request

class AuthSignupHomeRole(AuthSignupHome):

    def get_auth_signup_qcontext(self):
        qcontext = super().get_auth_signup_qcontext()
        qcontext['signup_role'] = request.params.get('signup_role', 'User')
        qcontext['experience'] = request.params.get('experience')
        # qcontext['service_fee'] = request.params.get('service_fee')
        qcontext['description'] = request.params.get('description')
        return qcontext

    def _prepare_signup_values(self, qcontext):
        values = super()._prepare_signup_values(qcontext)
        
        if qcontext.get('signup_role'):
            values['signup_role'] = qcontext.get('signup_role')
            
        if qcontext.get('experience'):
            try:
                values['experience'] = int(qcontext.get('experience'))
            except ValueError:
                pass
                
        # if qcontext.get('service_fee'):
        #     try:
        #         values['service_fee'] = float(qcontext.get('service_fee'))
        #     except ValueError:
        #         pass
                
        if qcontext.get('description'):
            values['description'] = qcontext.get('description')
            
        # Process profile photo if uploaded
        profile_image = request.httprequest.files.get('profile_image')
        if profile_image:
            image_data = profile_image.read()
            if image_data:
                values['image_1920'] = base64.b64encode(image_data)
                
        return values
