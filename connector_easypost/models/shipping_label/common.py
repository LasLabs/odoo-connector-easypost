# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields

from odoo.addons.component.core import Component


class EasypostShippingLabel(models.Model):
    """ Binding Model for the Easypost ShippingLabel """
    _name = 'easypost.shipping.label'
    _inherit = 'easypost.binding'
    _inherits = {'shipping.label': 'odoo_id'}
    _description = 'Easypost ShippingLabel'
    _easypost_model = 'Shipment'

    odoo_id = fields.Many2one(
        comodel_name='shipping.label',
        string='ShippingLabel',
        required=True,
        ondelete='cascade',
    )
    rate_id = fields.Many2one(
        string='Rate',
        comodel_name='stock.picking.rate',
    )
    tracking_url = fields.Char(
        related='package_id.parcel_tracking_uri',
    )
    tracking_number = fields.Char(
        string='Tracking Number',
        related='package_id.parcel_tracking',
    )


class ShippingLabel(models.Model):
    """ Adds the ``one2many`` relation to the Easypost bindings
    (``easypost_bind_ids``)
    """
    _inherit = 'shipping.label'

    easypost_bind_ids = fields.One2many(
        comodel_name='easypost.shipping.label',
        inverse_name='odoo_id',
        string='Easypost Bindings',
    )


class ShippingLabelAdapter(Component):
    """ Backend Adapter for the Easypost ShippingLabel """
    _name = 'easypost.shipping.label.adapter'
    _inherit = 'easypost.adapter'
    _apply_on = 'easypost.shipping.label'
