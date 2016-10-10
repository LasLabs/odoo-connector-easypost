# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'EastPost Connector',
    'description': 'Provides EasyPost connection for rate quotes & purchase',
    'version': '9.0.1.0.0',
    'category': 'Connector',
    'author': "LasLabs",
    'license': 'AGPL-3',
    'website': 'https://laslabs.com',
    'depends': [
        'stock',
        'connector',
        'stock_picking_rate',
        'stock_picking_package_info',
        'base_delivery_carrier_label',
    ],
    "external_dependencies": {
        "python": [
            'easypost',
        ],
    },
    'data': [
        'views/easypost_backend_view.xml',
        'views/connector_menu.xml',
        'views/res_partner_view.xml',
        'views/stock_picking_package_view.xml',
        'wizards/easypost_address_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
