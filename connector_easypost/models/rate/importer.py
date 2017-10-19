# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

from ...components.mapper import eval_false


class EastypostRateImportMapper(Component):

    _name = 'easypost.import.mapper.rate'
    _inherit = 'easypost.import.mapper'
    _apply_on = 'easypost.rate'

    direct = [
        (eval_false('mode'), 'mode'),
        (eval_false('rate'), 'rate'),
        (eval_false('list_rate'), 'list_rate'),
        (eval_false('retail_rate'), 'retail_rate'),
        (eval_false('delivery_days'), 'delivery_days'),
        (eval_false('delivery_date_guaranteed'), 'is_guaranteed'),
        (eval_false('delivery_date'), 'date_delivery'),
    ]

    def _camel_to_title(self, camel_case):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_case)
        return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)

    def _get_currency_id(self, name):
        return self.env['res.currency'].search([
            ('name', '=', name),
        ],
            limit=1,
        )

    @mapping
    @only_create
    def rate_currency_id(self, record):
        return {'rate_currency_id': self._get_currency_id(record.currency).id}

    @mapping
    @only_create
    def retail_rate_currency_id(self, record):
        return {
            'retail_rate_currency_id':
                self._get_currency_id(record.retail_currency).id,
        }

    @mapping
    @only_create
    def list_rate_currency_id(self, record):
        return {
            'list_rate_currency_id':
                self._get_currency_id(record.list_currency).id,
        }

    @mapping
    @only_create
    def service_id(self, record):
        Services = self.env['delivery.carrier']
        Partners = self.env['res.partner']
        partner = Partners.search([
            ('name', '=', record.carrier),
            ('is_carrier', '=', True),
        ],
            limit=1,
        )
        if not partner:
            partner = Partners.create({
                'name': record.carrier,
                'is_carrier': True,
                'customer': False,
                'supplier': True,
            })
        service = Services.search([
            ('partner_id', '=', partner.id),
            ('easypost_service', '=', record.service),
            ('delivery_type', '=', 'easypost'),
        ],
            limit=1,
        )
        if not service:
            name = '%s - %s' % (
                partner.name,
                self._camel_to_title(record.service),
            )
            service = Services.create({
                'name': name,
                'delivery_type': 'easypost',
                'partner_id': partner.id,
                'easypost_service': record.service,
                'integration_level': 'rate_and_ship',
                'prod_environment': True,
                'active': True,
            })
        return {'service_id': service.id}

    @mapping
    @only_create
    def picking_id(self, record):
        picking_id = self.binder_for('easypost.shipment').to_odoo(
            record.shipment_id, unwrap=True, browse=False
        )
        return {'picking_id': picking_id}

    @mapping
    @only_create
    def package_id(self, record):
        package_id = self.binder_for('easypost.parcel').to_odoo(
            record.parcel.id, unwrap=True, browse=False
        )
        return {'package_id': package_id}


class EasypostRateImporter(Component):
    _name = 'easypost.importer.rate'
    _inherit = 'easypost.importer'
    _apply_on = 'easypost.rate'
