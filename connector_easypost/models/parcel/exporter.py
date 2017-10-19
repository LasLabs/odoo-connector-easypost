# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping


class ParcelExportMapper(Component):

    _name = 'easypost.export.mapper.parcel'
    _inherit = 'easypost.export.mapper'
    _apply_on = 'easypost.parcel'

    def _convert_to_inches(self, uom_qty, uom):
        inches = self.env.ref('product.product_uom_inch')
        if uom.id != inches.id:
            return uom._compute_quantity(
                uom_qty, inches,
            )
        else:
            return uom_qty

    def _convert_to_ounces(self, uom_qty, uom):
        oz = self.env.ref('product.product_uom_oz')
        if uom.id != oz.id:
            return uom._compute_quantity(
                uom_qty, oz,
            )
        else:
            return uom_qty

    @mapping
    @changed_by('length', 'length_uom_id')
    # pylint: disable=W8105
    def length(self, record):
        length = self._convert_to_inches(
            record.length,
            record.length_uom_id,
        )
        return {'length': length}

    @mapping
    @changed_by('width', 'width_uom_id')
    def width(self, record):
        width = self._convert_to_inches(
            record.width,
            record.width_uom_id,
        )
        return {'width': width}

    @mapping
    @changed_by('height', 'height_uom_id')
    def height(self, record):
        height = self._convert_to_inches(
            record.height,
            record.height_uom_id,
        )
        return {'height': height}

    @mapping
    @changed_by('total_weight', 'weight', 'weight_uom_id')
    def weight(self, record):
        """ Lookup the actual picking weight as the record weight
        only accounts for the weight of the packaging """
        weight = self._convert_to_ounces(
            record.shipping_weight or record.total_weight,
            record.weight_uom_id,
        )
        return {'weight': weight}

    @mapping
    @changed_by('shipper_package_code')
    def predefined_package(self, record):
        package = record.packaging_id
        if package.shipper_package_code:
            return {
                'predefined_package': package.shipper_package_code,
            }


class StockQuantPackageExporter(Component):
    _name = 'easypost.parcel.record.exporter'
    _inherit = 'easypost.exporter'
    _apply_on = 'easypost.parcel'
