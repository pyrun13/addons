# -*- coding: utf-8 -*-
{
    'name': "mrp_extend",
    'summary': """制造扩展模块""",
    'author': "Cognichain",
    'website': "http://www.cognichain.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'mrp', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_bom_views.xml',
        'views/mrp_production_views.xml',
        'views/modify_material_wizard_views.xml',
        'views/sale_order_views.xml',
        'views/stock_picking_views.xml',
        'views/production_material_statistics_views.xml',
    ],
    'demo': [
    ],
}