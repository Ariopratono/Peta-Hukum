# peraturan_merger/wizards/wizard_merge.py
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime

class PeraturanMergeWizard(models.TransientModel):
    _name = 'peraturan.merge.wizard'
    _description = 'Wizard Merge Peraturan'

    rule_id = fields.Many2one('peraturan.rule', string='Peraturan', required=True)
    version_ids = fields.Many2many('peraturan.version', string='Versi', domain="[('rule_id','=',rule_id)]", required=True)
    mode = fields.Selection([('annotated','Annotated (default)'), ('final','Final only'), ('history','Full history')], default='annotated')

    def action_merge(self):
        if not self.version_ids:
            raise UserError('Pilih minimal satu versi untuk digabung.')
        cons = self.env['peraturan.consolidation'].create({
            'name': f'Consolidation {self.rule_id.name} {datetime.now().strftime("%Y%m%d%H%M%S")}',
            'rule_id': self.rule_id.id,
            'version_ids': [(6,0,self.version_ids.ids)]
        })
        cons.action_generate(mode=self.mode)
        # return action to download file
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/peraturan.consolidation/{cons.id}/file/{cons.file_name}?download=true',
            'target': 'self',
        }
