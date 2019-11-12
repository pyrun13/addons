from odoo import models, fields, api


class ProductionMaterialStatistics(models.Model):
    _name = 'production.material.statistics'
    _description = '生产单物料统计'

    production_id = fields.Many2one('mrp.production', string='生产单')
    product_id = fields.Many2one('product.product', string='产品')
    demand_qty = fields.Float(string='需求数量')
    picking_balance = fields.Float(string='差额领料', compute='_compute_picking_balance')
    received_qty = fields.Float(string='已领料', compute='_compute_received_qty')
    done_qty = fields.Float(string='已消耗')
    scrap_qty = fields.Float(string='已报废')
    material_unbalance = fields.Boolean(string='物料不平衡', compute='_compute_material_unbalance')

    @api.depends('production_id')
    def _compute_material_unbalance(self):
        for record in self:
            flag = False
            if record.production_id.state == 'done':
                a = record.demand_qty + record.picking_balance
                b = record.received_qty
                c = record.done_qty + record.scrap_qty
                if a != b or a != c or b != c:
                    flag = True
            record.material_unbalance = flag

    @api.depends('production_id')
    def _compute_picking_balance(self):
        for record in self:
            record.picking_balance = record.get_picking_balance_value()

    def get_picking_balance_value(self, is_done=False):
        value = 0
        if self.production_id:
            for each_picking in self.production_id.material_stock_picking_ids:
                flag = True
                if is_done is True and each_picking.state != 'done':
                    flag = False
                if flag:
                    for each_line in each_picking.move_ids_without_package:
                        if each_line.product_id == self.product_id:
                            if each_picking.material_stock_picking_type == 'supplement':
                                value += each_line.product_uom_qty
                            elif each_picking.material_stock_picking_type == 'return':
                                value -= each_line.product_uom_qty
        return value

    @api.depends('production_id')
    def _compute_received_qty(self):
        for record in self:
            value = 0
            if record.production_id:
                stock_picking = record.production_id.get_stock_picking()
                if stock_picking and stock_picking.state == 'done':
                    for each_line in stock_picking.move_line_ids_without_package:
                        if each_line.product_id == record.product_id:
                            value += each_line.qty_done
            record.received_qty = value + record.get_picking_balance_value(is_done=True)

