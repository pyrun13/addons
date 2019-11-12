from odoo import models, fields, api


class ModifyMaterialWizard(models.TransientModel):
    _name = 'modify.material.wizard'

    type = fields.Selection([('supplement', '补料'), ('return', '退料')], string='操作类别')
    line_ids = fields.One2many('modify.material.wizard.detail', 'order_id', string='组件')

    def action_confirm(self):
        context = dict(self._context)
        obj = self.env.get('mrp.production').search([('id','=', context['active_id'])])
        supplement_list = []
        return_list = []
        for each_line in self.line_ids:
            if each_line.qty > 0:
                supplement_list.append([each_line.product_id.id, each_line.qty, each_line.product_uom.id])
            elif each_line.qty < 0:
                return_list.append([each_line.product_id.id, each_line.qty, each_line.product_uom.id])
        stock_picking = obj.get_stock_picking()
        value = {
            'origin': stock_picking.origin,
            'company_id': stock_picking.company_id.id,
            'user_id': False,
            'move_type': stock_picking.move_type,
            'partner_id': stock_picking.partner_id.id,
            'picking_type_id': stock_picking.picking_type_id.id,
            'move_ids_without_package': [(0, 0, {})]
        }
        if supplement_list:
            move_ids_value = self.get_move_ids_value(supplement_list, stock_picking)
            value.update({
                'material_stock_picking_type': 'supplement',
                'location_id': stock_picking.location_id.id,
                'location_dest_id': stock_picking.location_dest_id.id,
                'move_ids_without_package': move_ids_value,
            })
            obj.material_stock_picking_ids += self.env.get('stock.picking').sudo().create(value)
        if return_list:
            move_ids_value = self.get_move_ids_value(return_list, stock_picking, return_flag=True)
            value.update({
                'material_stock_picking_type': 'return',
                'location_id': stock_picking.location_dest_id.id,
                'location_dest_id': stock_picking.location_id.id,
                'move_ids_without_package': move_ids_value,
            })
            obj.material_stock_picking_ids += self.env.get('stock.picking').sudo().create(value)

    def get_move_ids_value(self, value_list, stock_picking, return_flag=False):
        move_ids_value = []
        for each_item in value_list:
            move_ids_value.append((0, 0, {
                'name': '物料调拨',
                'product_id': each_item[0],
                'product_uom_qty': abs(each_item[1]),
                'product_uom': each_item[2],
                'company_id': stock_picking.company_id.id,
                'picking_type_id': stock_picking.picking_type_id.id,
                'location_id': stock_picking.location_id.id if return_flag is False else stock_picking.location_dest_id.id,
                'location_dest_id': stock_picking.location_dest_id.id if return_flag is False else stock_picking.location_id.id,
            }))
        return move_ids_value


class ModifyMaterialWizardDetail(models.TransientModel):
    _name = 'modify.material.wizard.detail'

    order_id = fields.Many2one('modify.material.wizard', string='单据')
    product_id = fields.Many2one('product.product', string='组件')
    qty = fields.Float(string='数量')
    product_uom = fields.Many2one('uom.uom', '单位')


