# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.addons.connector.event import (on_record_create)
from openerp.addons.connector.queue.job import job
from ..connector import get_environment
from ..models.stock_picking import EasypostStockPickingAdapter


class ShippingLabelNew(models.TransientModel):
    """ Create a new shipping label.
    This wizard should be monitored by external connectors for creation. They
    can then implicitly determine the interface to purchase shipment over
    based on the ``rate_id`` attribute
    """
    _name = 'shipping.label.new'
    _description = 'Shipping Label New'

    easypost_binding_id = fields.Many2one(
        comodel_name='easypost.stock.picking.dispatch.rate',
        compute=lambda s: s._compute_rate_easypost_id(),
        required=True,
    )
    picking_id = fields.Many2one(
        string='Stock Picking',
        comodel_name='stock.picking',
        readonly=True,
        default=lambda s: s.env.context.get('active_id'),
    )
    rate_id = fields.Many2one(
        string='Rate',
        comodel_name='stock.picking.dispatch.rate',
        required=True,
    )

    @api.multi
    def action_trigger_label(self):
        """ Inherit this in connector interfaces if custom processing
        is needed before label purchase. No label is actually created
        in this method though, as the connector should fire and use the
        rate_id for its processing.
        """
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def _compute_rate_easypost_id(self):
        for rec_id in self:
            rate_id = self.env['easypost.stock.picking.dispatch.rate'].search([
                ('odoo_id', '=', rec_id.rate_id.id),
            ],
                limit=1,
            )
            rec_id.easypost_binding_id = rate_id.id


@job(default_channel='root.easypost')
@on_record_create(model_names=['shipping.label.new'])
def immediate_buy_shipment(session, model_name, record_id, vals):
    """ Trigger immediate purchase workflow for a Shipment """
    record = session.env[model_name].browse(record_id)
    env = get_environment(
        session,
        'easypost.stock.picking',
        record.easypost_binding_id.backend_id.id,
    )
    unit = env.get_connector_unit(EasypostStockPickingAdapter)
    return unit.buy(record.rate_id)
