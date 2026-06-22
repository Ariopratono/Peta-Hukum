# -*- coding: utf-8 -*-
import base64
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class LegalCustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(LegalCustomerPortal, self)._prepare_portal_layout_values()
        user = request.env.user
        values['user'] = user
        return values

    @http.route(['/my/expert-profile'], type='http', auth='user', website=True)
    def expert_profile(self, **post):
        user = request.env.user
        # If they are just 'User', redirect them to user profile
        if user.signup_role == 'User':
            return request.redirect('/my/user-profile')
            
        values = self._prepare_portal_layout_values()
        values['page_name'] = 'expert_profile'
        
        if request.httprequest.method == 'POST':
            expert_vals = {}
            if 'name' in post:
                expert_vals['name'] = post.get('name')
            if 'phone' in post:
                expert_vals['phone'] = post.get('phone')
            if 'experience' in post:
                try:
                    expert_vals['experience'] = int(post.get('experience'))
                except ValueError:
                    pass
            if 'description' in post:
                expert_vals['description'] = post.get('description')
                
            profile_image = request.httprequest.files.get('profile_image')
            if profile_image:
                image_data = profile_image.read()
                if image_data:
                    expert_vals['image_1920'] = base64.b64encode(image_data)
                    
            if expert_vals:
                user.sudo().write(expert_vals)
                values['success_message'] = "Profile updated successfully!"

        return request.render("legal_website.portal_expert_profile", values)

    @http.route(['/my/user-profile'], type='http', auth='user', website=True)
    def user_profile(self, **post):
        user = request.env.user
        # If they are an expert, redirect them to expert profile
        if user.signup_role and user.signup_role != 'User':
            return request.redirect('/my/expert-profile')

        values = self._prepare_portal_layout_values()
        values['page_name'] = 'user_profile'
        
        if request.httprequest.method == 'POST':
            user_vals = {}
            if 'name' in post:
                user_vals['name'] = post.get('name')
            if 'phone' in post:
                user_vals['phone'] = post.get('phone')
                
            profile_image = request.httprequest.files.get('profile_image')
            if profile_image:
                image_data = profile_image.read()
                if image_data:
                    user_vals['image_1920'] = base64.b64encode(image_data)
                    
            if user_vals:
                user.sudo().write(user_vals)
                values['success_message'] = "Profile updated successfully!"

        return request.render("legal_website.portal_user_profile", values)
