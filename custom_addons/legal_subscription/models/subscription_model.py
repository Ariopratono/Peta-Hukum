# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta


class SubscriptionPlan(models.Model):
    _name = 'legal.subscription.plan'
    _description = 'Legal Subscription Plan'
    _rec_name = 'name'

    name = fields.Char('Plan Name', required=True)
    description = fields.Text('Description')
    price = fields.Float('Monthly Price', default=0.0)
    search_limit = fields.Integer('Daily Search Limit', default=5)
    features = fields.Text('Features List')
    is_active = fields.Boolean('Active', default=True)


class UserSubscription(models.Model):
    _name = 'legal.user.subscription'
    _description = 'User Subscription'
    _rec_name = 'plan_id'

    user_id = fields.Many2one('res.users', 'User', required=True)
    plan_id = fields.Many2one('legal.subscription.plan', 'Plan', required=True)
    start_date = fields.Date('Start Date', default=fields.Date.today)
    end_date = fields.Date('End Date')
    is_active = fields.Boolean('Active', default=True)
    
    @api.model
    def create(self, vals):
        if 'end_date' not in vals:
            start_date = fields.Date.from_string(vals.get('start_date', fields.Date.today()))
            vals['end_date'] = start_date + timedelta(days=30)
        return super().create(vals)