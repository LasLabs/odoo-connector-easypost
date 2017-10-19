# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component


class EasypostSaleImportMapper(Component):

    _name = 'easypost.import.mapper.sale'
    _inherit = 'easypost.import.mapper'
    _apply_on = 'easypost.sale'


class EasypostSaleImporter(Component):

    _name = 'easypost.shipment.record.sale'
    _inherit = 'easypost.importer'
    _apply_on = 'easypost.sale'
