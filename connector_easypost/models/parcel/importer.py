# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.component.core import Component


class ParcelImportMapper(Component):

    _name = 'easypost.import.mapper.parcel'
    _inherit = 'easypost.import.mapper'
    _apply_on = 'easypost.parcel'

    _direct = [
        ('length', 'length_float'),
        ('width', 'width_floath'),
        ('height', 'height_float'),
        ('weight', 'total_weight'),
    ]


class StockQuantPackageImporter(Component):
    _name = 'easypost.parcel.record.importer'
    _inherit = 'easypost.importer'
    _apply_on = 'easypost.parcel'
