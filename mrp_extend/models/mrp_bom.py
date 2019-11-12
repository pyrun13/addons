from odoo import models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    def explode(self, product, quantity, picking_type=False):
        boms_done, lines_done = super(MrpBom, self).explode(product, quantity, picking_type)
        for each_line in lines_done:
            qty = each_line[1].get('qty', 0)
            attrition_rate = each_line[0].attrition_rate/100
            if qty and attrition_rate:
                each_line[1]['qty'] = qty / (1 - attrition_rate)
        return boms_done, lines_done
