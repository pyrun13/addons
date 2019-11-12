from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    material_stock_picking_type = fields.Selection([('supplement', '补料'), ('return', '退料')], string='物料调拨类型')
