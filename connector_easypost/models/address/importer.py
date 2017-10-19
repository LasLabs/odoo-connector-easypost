# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

from ...components.mapper import eval_false


class EasypostAddressImportMapper(Component):

    _name = 'easypost.import.mapper.address'
    _inherit = 'easypost.import.mapper'
    _apply_on = 'easypost.address'

    direct = [
        (eval_false('street1'), 'street'),
        (eval_false('street2'), 'street2'),
        (eval_false('city'), 'city'),
        (eval_false('zip'), 'zip'),
    ]

    @mapping
    @only_create
    def odoo_id(self, record):
        """Handle multiple validations in a row."""
        existing = self.env[self._apply_on].search([
            ('backend_id', '=', self.backend_record.id),
            ('external_id', '=', record.id),
        ])
        if existing:
            return {'odoo_id': existing.id}

    @mapping
    @only_create
    def partner_id(self, record):
        binder = self.binder_for(record._name)
        address_id = binder.to_odoo(record.id, browse=True)
        return {'partner_id': address_id.partner_id.id}

    @mapping
    def country_state_id(self, record):
        country_id = self.env['res.country'].search([
            ('code', '=', record.country),
        ],
            limit=1,
        )
        state_id = self.env['res.country.state'].search([
            ('country_id', '=', country_id.id),
            ('code', '=', record.state),
        ],
            limit=1,
        )
        return {'country_id': country_id.id,
                'state_id': state_id.id,
                }

    @mapping
    def validation_messages(self, record):
        messages = []
        for e in record.verifications.delivery.errors:
            messages.append(e.message)
        return {'validation_messages': ', '.join(messages)}

    @mapping
    def is_valid(self, record):
        return {'is_valid': record.verifications.delivery.success}


class EasypostAddressImporter(Component):

    _name = 'easypost.importer.address'
    _inherit = 'easypost.importer'
    _apply_on = 'easypost.address'

    def _is_uptodate(self, binding):
        """Return False to always force import """
        return False
