# -*- coding: utf-8 -*-

from odoo import http, fields
from odoo.http import request
from datetime import datetime, timedelta
import json


class SubscriptionController(http.Controller):

    @http.route('/subscription/debug', type='http', auth="public", website=True)
    def subscription_debug(self, **kwargs):
        """Debug subscription controller"""
        return "<h1>Subscription Controller Working!</h1><p>Controller is loaded correctly.</p>"

    @http.route('/subscription/pricing', type='http', auth="public", website=True)
    def subscription_pricing(self, **kwargs):
        """Halaman pricing plans"""
        try:
            subscription_plans = request.env['subscription.plan'].sudo().search([])
            
            return request.render('legal_website.pricing_page', {
                'subscription_plans': subscription_plans
            })
        except Exception as e:
            return "<h1>Debug Error</h1><p>Error: %s</p>" % str(e)

    @http.route('/subscription/checkout', type='http', auth="public", website=True)
    def subscription_checkout(self, plan_id=None, **kwargs):
        """Halaman checkout"""
        if not plan_id:
            return request.redirect('/subscription/pricing')
        
        try:
            plan_id = int(plan_id)
            subscription_plan = request.env['subscription.plan'].sudo().browse(plan_id)
            if not subscription_plan.exists():
                return request.redirect('/subscription/pricing')
                
            return request.render('legal_website.checkout_page', {
                'subscription_plan': subscription_plan
            })
        except (ValueError, TypeError):
            return request.redirect('/subscription/pricing')

    @http.route('/subscription/process_checkout', type='http', auth="public", website=True, methods=['POST'], csrf=True)
    def process_checkout(self, **post):
        """Proses checkout dan buat subscription"""
        try:
            plan_id = int(post.get('plan_id'))
            subscription_plan = request.env['subscription.plan'].sudo().browse(plan_id)
            
            if not subscription_plan.exists():
                return request.redirect('/subscription/pricing')
            
            # Buat user subscription
            user = request.env.user
            
            # Cek apakah user sudah login
            if user._is_public():
                # Jika belum login, redirect ke login
                return request.redirect('/web/login?redirect=/subscription/checkout?plan_id=%s' % plan_id)
            
            # Cek apakah user sudah punya subscription aktif untuk plan ini
            existing_subscription = request.env['user.subscription'].sudo().search([
                ('user_id', '=', user.id),
                ('plan_id', '=', plan_id),
                ('is_active', '=', True)
            ])
            
            if existing_subscription:
                # Redirect ke success page jika sudah berlangganan
                return request.redirect('/subscription/success?subscription_id=%s' % existing_subscription.id)
            
            # Buat subscription baru
            start_date = fields.Date.today()
            end_date = start_date + timedelta(days=30)  # 30 hari
            
            subscription = request.env['user.subscription'].sudo().create({
                'user_id': user.id,
                'plan_id': plan_id,
                'start_date': start_date,
                'end_date': end_date,
                'is_active': True,
                'usage_count': 0
            })
            
            # Redirect ke success page
            return request.redirect('/subscription/success?subscription_id=%s' % subscription.id)
            
        except Exception as e:
            # Log error dan redirect kembali ke pricing
            request.env['ir.logging'].sudo().create({
                'name': 'Subscription Checkout Error',
                'type': 'server',
                'level': 'ERROR',
                'message': str(e),
                'path': request.httprequest.path,
                'func': 'process_checkout'
            })
            return request.redirect('/subscription/pricing?error=checkout_failed')

    @http.route('/subscription/success', type='http', auth="user", website=True)
    def subscription_success(self, subscription_id=None, **kwargs):
        """Halaman sukses setelah checkout"""
        if not subscription_id:
            return request.redirect('/subscription/pricing')
        
        try:
            subscription_id = int(subscription_id)
            subscription = request.env['user.subscription'].sudo().search([
                ('id', '=', subscription_id),
                ('user_id', '=', request.env.user.id)
            ])
            
            if not subscription:
                return request.redirect('/subscription/pricing')
                
            return request.render('legal_website.success_page', {
                'subscription': subscription
            })
        except (ValueError, TypeError):
            return request.redirect('/subscription/pricing')

    @http.route('/my/subscriptions', type='http', auth="user", website=True)
    def my_subscriptions(self, **kwargs):
        """Halaman kelola subscription user"""
        user = request.env.user
        user_subscriptions = request.env['user.subscription'].sudo().search([
            ('user_id', '=', user.id)
        ], order='create_date desc')
        
        return request.render('legal_website.my_subscriptions_page', {
            'user_subscriptions': user_subscriptions
        })

    @http.route('/subscription/cancel/<int:subscription_id>', type='http', auth="user", website=True, methods=['POST'], csrf=True)
    def cancel_subscription(self, subscription_id, **kwargs):
        """Cancel subscription"""
        subscription = request.env['user.subscription'].sudo().search([
            ('id', '=', subscription_id),
            ('user_id', '=', request.env.user.id)
        ])
        
        if subscription:
            subscription.is_active = False
            
        return request.redirect('/my/subscriptions')

    @http.route('/api/subscription/check', type='json', auth="user")
    def check_subscription(self, **kwargs):
        """API untuk cek status subscription user"""
        user = request.env.user
        
        # Cari active subscription
        active_subscription = request.env['user.subscription'].sudo().search([
            ('user_id', '=', user.id),
            ('is_active', '=', True),
            ('start_date', '<=', fields.Date.today()),
            ('end_date', '>=', fields.Date.today())
        ], limit=1)
        
        if active_subscription:
            return {
                'has_subscription': True,
                'plan_name': active_subscription.plan_id.name,
                'search_limit': active_subscription.plan_id.search_limit,
                'usage_count': active_subscription.usage_count,
                'advanced_search': active_subscription.plan_id.advanced_search,
                'legal_consultation': active_subscription.plan_id.legal_consultation,
                'priority_support': active_subscription.plan_id.priority_support
            }
        else:
            return {
                'has_subscription': False,
                'search_limit': 5,  # Default limit untuk free user
                'usage_count': 0
            }

    @http.route('/api/subscription/increment_usage', type='json', auth="user")
    def increment_usage(self, **kwargs):
        """API untuk increment usage count"""
        user = request.env.user
        
        # Cari active subscription
        active_subscription = request.env['user.subscription'].sudo().search([
            ('user_id', '=', user.id),
            ('is_active', '=', True),
            ('start_date', '<=', fields.Date.today()),
            ('end_date', '>=', fields.Date.today())
        ], limit=1)
        
        if active_subscription:
            # Reset usage count jika hari baru
            today = fields.Date.today()
            if active_subscription.last_usage_date != today:
                active_subscription.usage_count = 0
                active_subscription.last_usage_date = today
            
            # Increment usage
            active_subscription.usage_count += 1
            
            return {
                'success': True,
                'usage_count': active_subscription.usage_count,
                'search_limit': active_subscription.plan_id.search_limit
            }
        else:
            return {
                'success': False,
                'message': 'No active subscription'
            }