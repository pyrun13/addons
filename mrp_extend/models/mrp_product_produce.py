from odoo import models

class MrpProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    def _record_production(self):
        self.update_mrp_production_material_statistics()
        return super(MrpProductProduce, self)._record_production()

    def update_mrp_production_material_statistics(self):
        """生产单生产后，更新生产单的物料统计"""
        value_dict = {}
        for each_line in self.raw_workorder_line_ids:
            product_id = each_line.product_id.id
            if product_id not in value_dict:
                value_dict[product_id] = each_line.qty_done
            else:
                value_dict[product_id] += each_line.qty_done
        if value_dict:
            for each_product_id in value_dict:
                objs = self.production_id.material_statistics_ids.filtered(lambda u: u.product_id.id == each_product_id)
                for each_obj in objs:
                    each_obj.done_qty += value_dict[each_product_id]
