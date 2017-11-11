# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping


class EasypostSaleExportMapper(Component):

    _name = 'easypost.export.mapper.sale'
    _inherit = 'easypost.export.mapper.shipment'
    _apply_on = 'easypost.sale'

    @mapping
    @changed_by('order_line')
    def parcel(self, record):
        # Estimate based on a cube package
        weight = 0.0
        volume = 0.0
        for line in record.order_line:
            weight += line.product_id.weight_oz * line.product_uom_qty
            volume += line.product_id.volume_in * line.product_uom_qty
        cube_side = volume ** (1.0/2.0)
        return {
            'parcel': {
                'length': cube_side,
                'width': cube_side,
                'height': cube_side,
                'weight': weight,
            },
        }

    @mapping
    @changed_by('partner_id')
    def to_address(self, record):
        return {'to_address': self._map_partner(record.partner_id)}

    @mapping
    @changed_by('location_id')
    def from_address(self, record):
        return {
            'from_address': self._map_partner(record.company_id.partner_id),
        }


class EasypostSaleExporter(Component):

    _name = 'easypost.sale.record.exporter'
    _inherit = 'easypost.exporter'
    _apply_on = 'easypost.sale'

    def _after_export(self):
        """Immediate re-import & expire old rates. """

        existing_rates = self.binding_record.carrier_rate_ids.filtered(
            lambda r: r.service_id.delivery_type == 'easypost'
        )
        existing_rates.unlink()

        for rate in self.easypost_record.rates:
            rate.parcel = self.easypost_record.parcel
            self.env['easypost.sale.rate'].import_direct(
                self.backend_record, rate,
            )
