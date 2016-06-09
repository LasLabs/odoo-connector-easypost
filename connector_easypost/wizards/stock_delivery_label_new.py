# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.addons.connector.event import (on_record_create)
from openerp.addons.connector.queue.job import job
from ..connector import get_environment
from ..models.shipment import EasypostShipmentAdapter


class StockDeliveryLabelNew(models.TransientModel):
    """ Triggers EasyPost purchase workflow on creation """
    _inherit = 'stock.delivery.label.new'

    easypost_binding_id = fields.Many2one(
        comodel_name='easypost.stock.delivery.rate',
        compute=lambda s: s._compute_rate_easypost_id(),
        required=True,
    )

    @api.multi
    def _compute_rate_easypost_id(self):
        for rec_id in self:
            rate_id = self.env['easypost.stock.delivery.rate'].search([
                ('odoo_id', '=', rec_id.id),
            ],
                limit=1,
            )
            rec_id.easypost_binding_id = rate_id.id


@job(default_channel='root.easypost')
@on_record_create(model_names=['stock.delivery.label.new'])
def immediate_buy_shipment(session, model_name, record_id, vals):
    """ Trigger immediate purchase workflow for a Shipment """
    record = session.env[model_name].browse(record_id)
    env = get_environment(
        session,
        'easypost.easypost.shipment',
        record.easypost_binding_id.backend_id.id,
    )
    unit = env.get_connector_unit(EasypostShipmentAdapter)
    return unit.buy(record.rate_id)
