from odoo import models, fields, api, exceptions


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    attrition_rate = fields.Float(string='损耗率(%)')

    def write(self, vals):
        attrition_rate = vals.get('attrition_rate', 0)
        if attrition_rate < 0:
            raise exceptions.ValidationError('损耗率不能为负数！')
        return super(MrpBomLine, self).write(vals)
