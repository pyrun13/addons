from odoo import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    material_stock_picking_ids = fields.Many2many('stock.picking', 'material_stock_picking_rel', string='物料调拨')
    material_stock_picking_count = fields.Integer(string='物料调拨数量', compute='_compute_material_stock_picking_count')
    product_unit_price = fields.Monetary(string='产品单价', currency_field='product_unit_price_currency_id', compute='_compute_product_unit_price')
    product_unit_price_currency_id = fields.Many2one('res.currency', '产品单价币种', related='company_id.currency_id', readonly=True)
    material_statistics_ids = fields.One2many('production.material.statistics', 'production_id', string='物料统计')
    material_unbalance = fields.Boolean(string='物料不平衡', compute='_compute_material_unbalance')

    @api.depends('material_stock_picking_ids')
    def _compute_material_stock_picking_count(self):
        self.material_stock_picking_count = len(self.material_stock_picking_ids)

    @api.depends('material_statistics_ids')
    def _compute_material_unbalance(self):
        for record in self:
            flag = False
            for each_line in record.material_statistics_ids:
                if each_line.material_unbalance:
                    flag = True
                    break
            record.material_unbalance = flag

    def action_material_stock_move(self):
        self.ensure_one()
        new_context = dict(self._context) or {}
        line_data = []
        added_product_list = []
        for each_item in self.move_raw_ids:
            if each_item.product_id not in added_product_list:
                added_product_list.append(each_item.product_id)
                line_data.append((0, 0, {
                    'product_id': each_item.product_id.id,
                    'product_uom': each_item.product_uom.id,
                }))
        wizard = self.env.get('modify.material.wizard').create({
            'line_ids': line_data
        })
        return {
            'name': '物料调拨',
            'view_mode': 'form',
            'view_id': self.env.ref('mrp_extend.modify_material_wizard_view_form_1176').id,
            'res_model': wizard._name,
            'domain': [],
            'context': new_context,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': wizard.id,
        }

    def action_see_material_stock_picking(self):
        self.ensure_one()
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        if len(self.material_stock_picking_ids.ids) > 1:
            action['domain'] = [('id', 'in', self.material_stock_picking_ids.ids)]
        elif self.material_stock_picking_ids:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = self.material_stock_picking_ids.id
        action['context'] = dict(self._context, default_origin=self.name, create=False)
        return action

    @api.depends()
    def _compute_product_unit_price(self):
        for record in self:
            record.product_unit_price = 0
            objs = self.env.get('stock.valuation.layer').sudo().search(
                [('id', 'in', (record.move_raw_ids + record.move_finished_ids + record.scrap_ids.move_id).stock_valuation_layer_ids.ids)])
            amount, qty = 0, 0
            for each_obj in objs:
                if each_obj.product_id == record.product_id:
                    amount += each_obj.value
                    qty += each_obj.quantity
            if amount != 0 and qty != 0:
                record.product_unit_price = amount / qty

    def get_stock_picking(self):
        for each_route in self.env.get('stock.location.route').search([]):
            if len(each_route.rule_ids) == 3:
                stock_picking_location_id = each_route.rule_ids[0].location_src_id
                for each_stock_picking in self.picking_ids:
                    if each_stock_picking.location_id == stock_picking_location_id:
                        return each_stock_picking

    def action_confirm(self):
        result = super(MrpProduction, self).action_confirm()
        self.init_material_statistics()
        return result

    def init_material_statistics(self):
        """初始化生产单的物料统计"""
        self.ensure_one()
        value_dict = {}
        for each_line in self.move_raw_ids:
            product_id = each_line.product_id.id
            if product_id not in value_dict:
                value_dict[product_id] = each_line.product_uom_qty
            else:
                value_dict[product_id] += each_line.product_uom_qty
        for each_product_id in value_dict:
            self.env.get('production.material.statistics').sudo().create({
                'production_id': self.id,
                'product_id': each_product_id,
                'demand_qty': value_dict[each_product_id],
            })
