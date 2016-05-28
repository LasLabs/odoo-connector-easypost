# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class StockDeliveryNew(models.TransientModel):
    _inherit = 'stock.delivery.new'

    @api.multi
    def action_create_delivery(self):
        """ Trigger an EasyPost export on delivery creation """
        group_id = super(StockDeliveryNew, self).action_create_delivery()
        self.env['easypost.shipment'].create({
            'group_id': group_id.id,
        })
        return group_id
