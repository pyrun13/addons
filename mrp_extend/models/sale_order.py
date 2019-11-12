from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _default_domain_customer_ids(self):
        customer_ids = self.env.get('res.partner').search([('customer_rank', '>', 0)])
        objs = self.env.get('res.partner')
        for each_item in customer_ids:
            if each_item.user_id.id == self.env.uid:
                objs += each_item
        return objs

    domain_customer_ids = fields.Many2many('res.partner', 'sale_order_res_partner_domain_customer_rel', string='客户过滤',
                                           default=_default_domain_customer_ids, compute='_compute_domain_customer_ids')

    @api.depends()
    def _compute_domain_customer_ids(self):
        for record in self:
            customer_ids = self.env.get('res.partner').search([('customer_rank', '>', 0)])
            for each_item in customer_ids:
                if each_item.user_id.id == self.env.uid:
                    record.domain_customer_ids += each_item
