# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping


class EasypostAddressExportMapper(Component):

    _name = 'easypost.export.mapper.address'
    _inherit = 'easypost.export.mapper'
    _apply_on = 'easypost.address'

    direct = [
        ('name', 'name'),
        ('company_name', 'company'),
        ('street_original', 'street1'),
        ('street2_original', 'street2'),
        ('city_original', 'city'),
        ('zip_original', 'zip'),
        ('phone', 'phone'),
        ('email', 'email'),
    ]

    @mapping
    def verify(self, record):
        return {'verify': ['delivery']}

    @mapping
    @changed_by('state_id')
    def state(self, record):
        if record.state_id_original:
            return {'state': record.state_id_original.code}

    @mapping
    @changed_by('country_id')
    def country(self, record):
        if record.country_id_original:
            return {'country': record.country_id_original.code}


class EasypostAddressExporter(Component):

    _name = 'easypost.address.record.exporter'
    _inherit = 'easypost.exporter'
    _apply_on = 'easypost.address'

    def _after_export(self):
        """ Immediate re-import """
        self.binding_record.import_direct(self.binding_record.backend_id,
                                          self.easypost_record)
