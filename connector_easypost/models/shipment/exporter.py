# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping


class EasypostShipmentExportMapper(Component):

    _name = 'easypost.export.mapper.shipment'
    _inherit = 'easypost.export.mapper'
    _apply_on = 'easypost.shipment'

    def _map_partner(self, partner_id):
        vals = {
            'name': partner_id.name,
            'street1': partner_id.street,
            'street2': partner_id.street2 or '',
            'email': partner_id.email or '',
            'phone': partner_id.phone or '',
            'city': partner_id.city,
            'zip': partner_id.zip,
            'state': partner_id.state_id.code,
            'country': partner_id.country_id.code,
        }
        if partner_id.company_id:
            vals['company'] = partner_id.company_id.name
        return vals

    @mapping
    @changed_by('package_ids')
    def parcel(self, record):
        if record.package_ids:
            binder = self.binder_for('easypost.parcel')
            parcel = binder.to_backend(record.package_ids[:1])
            return {'parcel': {'id': parcel}}

    @mapping
    @changed_by('partner_id')
    def to_address(self, record):
        return {'to_address': self._map_partner(record.partner_id)}

    @mapping
    @changed_by('location_id')
    def from_address(self, record):
        warehouse = self.env['stock.warehouse'].search([
            ('lot_stock_id', '=', record.location_id.id),
        ],
            limit=1,
        )
        partner = warehouse.partner_id or record.company_id.partner_id
        return {'from_address': self._map_partner(partner)}


class EasypostShipmentExporter(Component):

    _name = 'easypost.shipment.record.exporter'
    _inherit = 'easypost.exporter'
    _apply_on = 'easypost.shipment'

    def _after_export(self):
        """Immediate re-import & expire old rates. """

        # Existing EasyPost rates are now invalid.
        existing_rates = self.binding_record.dispatch_rate_ids.filtered(
            lambda r: (r.service_id.delivery_type == 'easypost' and
                       not r.date_purchased)
        )
        existing_rates.unlink()

        for rate in self.easypost_record.rates:
            rate.parcel = self.easypost_record.parcel
            self.env['easypost.rate'].import_direct(
                self.backend_record, rate,
            )
