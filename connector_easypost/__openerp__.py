# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
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
        'connector',
        'stock_delivery',
    ],
    "external_dependencies": {
        "python": [
            'easypost',
        ],
    },
    'data': [
        'views/easypost_backend_view.xml',
        'views/connector_menu.xml',
    ],
    'installable': True,
    'application': False,
}
