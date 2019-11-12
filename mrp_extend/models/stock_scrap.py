from odoo import models


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    def action_validate(self):
        self.ensure_one()
        self.update_mrp_production_material_statistics()
        return super(StockScrap, self).action_validate()

    def update_mrp_production_material_statistics(self):
        context = dict(self._context)
        if context.get('active_model') == 'mrp.production':
            production_obj = self.env.get('mrp.production').search([('id', '=', context.get('active_id'))])
            objs = production_obj.material_statistics_ids.filtered(lambda u: u.product_id.id == self.product_id.id)
            for each_obj in objs:
                each_obj.scrap_qty += self.scrap_qty
