# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import none


class EasypostShipmentImportMapper(Component):

    _name = 'easypost.import.mapper.shipment'
    _inherit = 'easypost.import.mapper'
    _apply_on = 'easypost.shipment'

    direct = [
        (none('refund_status'), 'refund_status'),
    ]


class EasypostShipmentImporter(Component):

    _name = 'easypost.shipment.record.importer'
    _inherit = 'easypost.importer'
    _apply_on = 'easypost.shipment'
