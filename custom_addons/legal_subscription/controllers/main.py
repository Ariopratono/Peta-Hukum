# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class LegalSubscriptionController(http.Controller):

    @http.route('/', website=True, auth='public')
    def home(self, **kw):
        """Homepage"""
        return request.render('legal_subscription.homepage')

    @http.route('/pricing', website=True, auth='public')
    def pricing(self, **kw):
        """Pricing page"""
        plans = request.env['legal.subscription.plan'].sudo().search([('is_active', '=', True)])
        return request.render('legal_subscription.pricing_page', {'plans': plans})

    @http.route('/subscribe/<int:plan_id>', website=True, auth='user')
    def subscribe(self, plan_id, **kw):
        """Subscribe to plan"""
        plan = request.env['legal.subscription.plan'].sudo().browse(plan_id)
        if plan.exists():
            # Create subscription
            request.env['legal.user.subscription'].sudo().create({
                'user_id': request.env.user.id,
                'plan_id': plan_id,
            })
            return request.render('legal_subscription.success_page', {'plan': plan})
        return request.redirect('/pricing')

    @http.route('/my-subscription', website=True, auth='user')
    def my_subscription(self, **kw):
        """User subscription dashboard"""
        subscriptions = request.env['legal.user.subscription'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ])
        return request.render('legal_subscription.my_subscription', {'subscriptions': subscriptions})