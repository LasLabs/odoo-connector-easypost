# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'EastPost Connector',
    'description': 'Provides EasyPost connection for rate quotes & purchase',
    'version': '10.0.1.0.0',
    'category': 'Connector',
    'author': "LasLabs",
    'license': 'AGPL-3',
    'website': 'https://laslabs.com',
    'depends': [
        'stock',
        'connector',
        'stock_picking_rate',
        'stock_package_info',
        'base_delivery_carrier_label',
    ],
    "external_dependencies": {
        "python": [
            'easypost',
        ],
    },
    'data': [
        'data/product_packaging_template.xml',
        'views/easypost_backend_view.xml',
        'views/connector_menu.xml',
        'views/res_partner_view.xml',
        'views/stock_picking_label_view.xml',
        'wizards/easypost_address_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
