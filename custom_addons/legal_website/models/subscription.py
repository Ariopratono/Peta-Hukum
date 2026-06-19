# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


class SubscriptionPlan(models.Model):
    _name = 'subscription.plan'
    _description = 'Subscription Plan'

    name = fields.Char('Plan Name', required=True)
    description = fields.Text('Description')
    price = fields.Float('Price per Month', default=0.0)
    search_limit = fields.Integer('Search Limit per Day', default=5)
    advanced_search = fields.Boolean('Advanced Search Features', default=False)
    legal_consultation = fields.Boolean('Legal Consultation Access', default=False)
    priority_support = fields.Boolean('Priority Support', default=False)
    is_active = fields.Boolean('Is Active', default=True)
    
    @api.model
    def get_free_plan(self):
        """Get free plan for non-subscribed users"""
        return self.search([('price', '=', 0)], limit=1)


class UserSubscription(models.Model):
    _name = 'user.subscription'
    _description = 'User Subscription'

    user_id = fields.Many2one('res.users', 'User', required=True, ondelete='cascade')
    plan_id = fields.Many2one('subscription.plan', 'Subscription Plan', required=True, ondelete='cascade')
    start_date = fields.Date('Start Date', required=True, default=fields.Date.today)
    end_date = fields.Date('End Date', required=True)
    is_active = fields.Boolean('Is Active', default=True)
    usage_count = fields.Integer('Daily Usage Count', default=0)
    last_usage_date = fields.Date('Last Usage Date')
    
    @api.model
    def create(self, vals):
        """Override create to set end_date automatically"""
        if 'end_date' not in vals and 'start_date' in vals:
            start_date = fields.Date.from_string(vals['start_date'])
            vals['end_date'] = start_date + timedelta(days=30)
        return super(UserSubscription, self).create(vals)
    
    def check_usage_limit(self):
        """Check if user has reached daily usage limit"""
        today = fields.Date.today()
        
        # Reset usage count if it's a new day
        if self.last_usage_date != today:
            self.usage_count = 0
            self.last_usage_date = today
        
        return self.usage_count < self.plan_id.search_limit
    
    def increment_usage(self):
        """Increment daily usage count"""
        today = fields.Date.today()
        
        # Reset usage count if it's a new day
        if self.last_usage_date != today:
            self.usage_count = 0
            self.last_usage_date = today
        
        self.usage_count += 1
    
    @api.model
    def get_user_active_subscription(self, user_id):
        """Get active subscription for user"""
        return self.search([
            ('user_id', '=', user_id),
            ('is_active', '=', True),
            ('start_date', '<=', fields.Date.today()),
            ('end_date', '>=', fields.Date.today())
        ], limit=1)
    
    @api.model
    def check_user_access(self, user_id, feature=None):
        """Check if user has access to specific features"""
        subscription = self.get_user_active_subscription(user_id)
        
        if not subscription:
            # Return free plan limitations
            free_plan = self.env['subscription.plan'].get_free_plan()
            return {
                'has_subscription': False,
                'search_limit': free_plan.search_limit if free_plan else 5,
                'advanced_search': False,
                'legal_consultation': False,
                'priority_support': False,
                'usage_count': 0
            }
        
        # Check usage limit
        can_use = subscription.check_usage_limit()
        
        result = {
            'has_subscription': True,
            'subscription_id': subscription.id,
            'plan_name': subscription.plan_id.name,
            'search_limit': subscription.plan_id.search_limit,
            'usage_count': subscription.usage_count,
            'can_use_today': can_use,
            'advanced_search': subscription.plan_id.advanced_search,
            'legal_consultation': subscription.plan_id.legal_consultation,
            'priority_support': subscription.plan_id.priority_support
        }
        
        if feature:
            if feature == 'advanced_search':
                result['has_access'] = subscription.plan_id.advanced_search
            elif feature == 'legal_consultation':
                result['has_access'] = subscription.plan_id.legal_consultation
            elif feature == 'priority_support':
                result['has_access'] = subscription.plan_id.priority_support
            else:
                result['has_access'] = True
        
        return result