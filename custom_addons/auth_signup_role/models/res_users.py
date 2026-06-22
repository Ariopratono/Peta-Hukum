from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    signup_role = fields.Selection([
        ('User', 'User'),
        ('LBH', 'LBH'),
        ('Lawyer', 'Lawyer'),
        ('Notaris', 'Notaris'),
        ('Kurator', 'Kurator'),
        # ('Hakim', 'Hakim'),
        # ('Jaksa', 'Jaksa'),
        # ('Polisi', 'Polisi'),
        # ('Konsultan Hukum Lainnya', 'Konsultan Hukum Lainnya')
    ], string='Role', default='User')
    
    experience = fields.Integer(string='Experience (Years)', default=0)
    # service_fee = fields.Float(string='Service Fee', default=0.0)
    description = fields.Text(string='Description')

    @api.model_create_multi
    def create(self, vals_list):
        users = super(ResUsers, self).create(vals_list)
        role_map = {
            'LBH': 'lbh',
            'Lawyer': 'lawyer',
            'Notaris': 'notary',
            'Kurator': 'curator',
            # 'Hakim': 'judge',
            # 'Jaksa': 'prosecutor',
            # 'Polisi': 'police',
            # 'Konsultan Hukum Lainnya': 'other'
        }
        for user in users:
            if user.signup_role in role_map:
                self.env['legal.expert'].sudo().create({
                    'user_id': user.id,
                    'role': role_map[user.signup_role],
                    'experience': user.experience,
                    # 'service_fee': user.service_fee,
                    'description': user.description or '',
                })
        return users

    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        role_map = {
            'LBH': 'lbh',
            'Lawyer': 'lawyer',
            'Notaris': 'notary',
            'Kurator': 'curator',
            # 'Hakim': 'judge',
            # 'Jaksa': 'prosecutor',
            # 'Polisi': 'police',
            # 'Konsultan Hukum Lainnya': 'other'
        }
        
        expert_fields = [
            'signup_role', 
            'experience', 
            # 'service_fee', 
            'description']
        if any(f in vals for f in expert_fields):
            for user in self:
                expert = self.env['legal.expert'].sudo().search([('user_id', '=', user.id)], limit=1)
                if user.signup_role in role_map:
                    expert_vals = {
                        'role': role_map[user.signup_role],
                        'experience': user.experience,
                        # 'service_fee': user.service_fee,
                        'description': user.description or '',
                    }
                    if expert:
                        expert.write(expert_vals)
                    else:
                        expert_vals['user_id'] = user.id
                        self.env['legal.expert'].sudo().create(expert_vals)
                else:
                    if expert:
                        expert.unlink()
        return res
