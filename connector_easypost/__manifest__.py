# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# pylint: disable=C8101
{
    'name': 'EasyPost Connector',
    'version': '10.0.1.0.0',
    'category': 'Connector, Delivery, Stock',
    'author': "LasLabs",
    'license': 'AGPL-3',
    'website': 'https://laslabs.com',
    'depends': [
        'base_delivery_carrier_label',
        'base_partner_validate_address',
        'connector',
        'delivery_package_wizard',
        'l10n_us_product',
        'l10n_us_uom_profile',
        'sale_delivery_rate',
        'stock_package_info',
    ],
    "external_dependencies": {
        "python": [
            'easypost',
        ],
    },
    'data': [
        'data/product_packaging_data.xml',
        'data/res_partner_data.xml',
        # Carrier depends on partner
        'data/delivery_carrier_data.xml',
        'views/delivery_carrier_view.xml',
        'views/easypost_backend_view.xml',
        'views/connector_menu.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/product_product_demo.xml',
        'demo/res_company_demo.xml',
        'demo/res_partner_demo.xml',
    ],
    'installable': True,
    'application': False,
}
