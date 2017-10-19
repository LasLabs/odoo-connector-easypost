# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import fields, models
from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class EasypostParcel(models.Model):
    """ Binding Model for the Easypost StockQuantPackage. """
    _name = 'easypost.parcel'
    _inherit = 'easypost.binding'
    _inherits = {'stock.quant.package': 'odoo_id'}
    _description = 'Easypost Parcel'
    _easypost_model = 'Parcel'

    odoo_id = fields.Many2one(
        comodel_name='stock.quant.package',
        string='StockQuantPackage',
        required=True,
        ondelete='cascade',
    )


class StockQuantPackage(models.Model):
    """ Adds the ``one2many`` relation to the Easypost bindings
    (``easypost_bind_ids``)
    """
    _inherit = 'stock.quant.package'

    easypost_bind_ids = fields.One2many(
        comodel_name='easypost.parcel',
        inverse_name='odoo_id',
        string='Easypost Bindings',
    )


class ParcelAdapter(Component):
    """ Backend Adapter for the Easypost StockQuantPackage """
    _name = 'easypost.parcel.adapter'
    _inherit = 'easypost.adapter'
    _apply_on = 'easypost.parcel'

    def update(self, _id, data):
        """Parcels are immutable; create a new one instead."""
        _logger.info('Parcel update with %s and %s', _id, data)
        return self.create(data)
