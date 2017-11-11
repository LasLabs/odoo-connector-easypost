# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons.component.core import Component


class EasypostRate(models.Model):
    """ Binding Model for the Easypost StockPickingRate """
    _name = 'easypost.rate'
    _inherit = 'easypost.binding'
    _inherits = {'stock.picking.rate': 'odoo_id'}
    _description = 'Easypost Rate'
    _easypost_model = 'Rate'

    odoo_id = fields.Many2one(
        comodel_name='stock.picking.rate',
        string='StockPickingRate',
        required=True,
        ondelete='cascade',
    )

    @api.multi
    def buy(self):
        with self.backend_id.work_on('easypost.shipment') as work:
            adapter = work.component(usage='backend.adapter')
            for rate in self.filtered(lambda r: not r.date_purchased):
                shipment = adapter.buy(rate)
                self.env['easypost.shipment'].import_direct(
                    self.backend_id, shipment,
                )
                self.env['easypost.shipping.label'].import_direct(
                    self.backend_id, shipment,
                )

    @api.multi
    def cancel(self):
        with self.backend_id.work_on('easypost.shipment') as work:
            adapter = work.component(usage='backend.adapter')
            for rate in self.filtered(lambda r: r.date_purchased):
                shipment = adapter.cancel(rate)
                self.env['easypost.shipment'].import_direct(
                    self.backend_id, shipment,
                )


class StockPickingRate(models.Model):
    """ Adds the ``one2many`` relation to the Easypost bindings
    (``easypost_bind_ids``)
    """
    _inherit = 'stock.picking.rate'

    easypost_bind_ids = fields.One2many(
        comodel_name='easypost.rate',
        inverse_name='odoo_id',
        string='Easypost Bindings',
    )

    @api.multi
    def buy(self):
        for binding in self.mapped('easypost_bind_ids'):
            binding.buy()
        return super(StockPickingRate, self).buy()

    @api.multi
    def cancel(self):
        for binding in self.mapped('easypost_bind_ids'):
            binding.cancel()
        return super(StockPickingRate, self).cancel()


class EasypostRateAdapter(Component):
    """ Backend Adapter for the Easypost StockPickingRate """
    _name = 'easypost.rate.adapter'
    _inherit = 'easypost.adapter'
    _apply_on = 'easypost.rate'
