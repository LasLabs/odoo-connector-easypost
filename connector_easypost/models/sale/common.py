# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo import models

from odoo.addons.component.core import Component


class EasypostSale(models.Model):
    """ Binding Model for the Easypost Sale """
    _name = 'easypost.sale'
    _inherit = 'easypost.binding'
    _inherits = {'sale.order': 'odoo_id'}
    _description = 'Easypost Sale'
    _easypost_model = 'Shipment'

    odoo_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale Order',
        required=True,
        ondelete='cascade',
    )


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    easypost_bind_ids = fields.One2many(
        comodel_name='easypost.sale',
        inverse_name='odoo_id',
        string='Easypost Bindings',
    )


class EasypostSaleAdapter(Component):
    """ Backend Adapter for the Easypost Sale """
    _name = 'easypost.sale.adapter'
    _inherit = 'easypost.adapter'
    _apply_on = 'easypost.sale'
