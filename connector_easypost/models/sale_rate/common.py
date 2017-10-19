# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons.component.core import Component


class EasypostSaleRate(models.Model):
    """ Binding Model for the Easypost StockPickingRate """
    _name = 'easypost.sale.rate'
    _inherit = 'easypost.binding'
    _inherits = {'delivery.carrier.rate': 'odoo_id'}
    _description = 'Easypost Sale Rate'
    _easypost_model = 'Rate'

    odoo_id = fields.Many2one(
        comodel_name='delivery.carrier.rate',
        string='Delivery Carrier Rate',
        required=True,
        ondelete='cascade',
    )


class DeliveryCarrierRate(models.Model):
    _inherit = 'delivery.carrier.rate'

    easypost_bind_ids = fields.One2many(
        comodel_name='easypost.sale.rate',
        inverse_name='odoo_id',
        string='Easypost Bindings',
    )

    @api.multi
    def generate_equiv_picking_rates(self, stock_picking):
        rates = super(DeliveryCarrierRate, self).generate_equiv_picking_rates(
            stock_picking,
        )
        stock_picking.easypost_bind_ids.ensure_bindings(
            stock_picking,
        )
        return rates


class EasypostSaleRateAdapter(Component):
    """ Backend Adapter for the Easypost StockPickingRate """
    _name = 'easypost.sale.rate.adapter'
    _inherit = 'easypost.adapter'
    _apply_on = 'easypost.sale.rate'
