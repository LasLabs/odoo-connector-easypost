# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create


class EastypostSaleRateImportMapper(Component):

    _name = 'easypost.import.mapper.sale.rate'
    _inherit = 'easypost.import.mapper.rate'
    _apply_on = 'easypost.sale.rate'

    @mapping
    @only_create
    def sale_order_id(self, record):
        sale_order_id = self.binder_for('easypost.sale').to_odoo(
            record.shipment_id, unwrap=True, browse=False
        )
        return {'sale_order_id': sale_order_id}

    @mapping
    @only_create
    def picking_id(self, record):
        """This is required to stub off the picking logic from parent."""
        return


class EasypostSaleRateImporter(Component):
    _name = 'easypost.importer.sale.rate'
    _inherit = 'easypost.importer'
    _apply_on = 'easypost.sale.rate'
