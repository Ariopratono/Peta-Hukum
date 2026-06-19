# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SystemMaintenance(models.TransientModel):
    _name = 'system.maintenance'
    _description = 'System Maintenance Control Panel'
    
    maintenance_mode = fields.Selection([
        ('normal', 'Normal Operation'),
        ('maintenance', 'Maintenance Mode'),
        ('restricted', 'Restricted Access')
    ], string='Maintenance Mode', default='normal')
    
    def apply_settings(self):
        """Apply maintenance settings"""
        return {'type': 'ir.actions.act_window_close'}