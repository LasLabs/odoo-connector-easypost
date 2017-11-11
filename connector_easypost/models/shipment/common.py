# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from odoo.addons.component.core import Component


class EasypostShipment(models.Model):
    """ Binding Model for the Easypost EasypostShipment """
    _name = 'easypost.shipment'
    _inherit = 'easypost.binding'
    _inherits = {'stock.picking': 'odoo_id'}
    _description = 'Easypost Shipment'
    _easypost_model = 'Shipment'

    odoo_id = fields.Many2one(
        comodel_name='stock.picking',
        string='StockPicking',
        required=True,
        ondelete='cascade',
    )
    refund_status = fields.Char()


class StockPicking(models.Model):
    """ Adds the ``one2many`` relation to the Easypost bindings
    (``easypost_bind_ids``)
    """
    _inherit = 'stock.picking'

    easypost_bind_ids = fields.One2many(
        comodel_name='easypost.shipment',
        inverse_name='odoo_id',
        string='Easypost Bindings',
    )

    @api.multi
    def generate_shipping_labels(self, packages=None):
        """ Add label generation for EasyPost """
        self.ensure_one()
        if self.carrier_id.delivery_type == 'easypost':
            if not isinstance(packages, type(self.env['stock.quant.package'])):
                packages = self.env['stock.quant.package'].browse(packages)
            return self.carrier_id.easypost_send_shipping(
                self, packages,
            )
        _super = super(StockPicking, self)
        return _super.generate_shipping_labels(package_ids=packages)


class EasypostShipmentAdapter(Component):
    """ Backend Adapter for the Easypost EasypostShipment """
    _name = 'easypost.shipment.adapter'
    _inherit = 'easypost.adapter'
    _apply_on = 'easypost.shipment'

    def buy(self, easypost_rate):
        """ Allows for purchasing of Rates through EasyPost
        :param rate: Unwrapped Odoo Rate record to purchase label for
        """

        easypost_shipment = self._get_shipment(easypost_rate)
        easypost_shipment = self.read(easypost_shipment.external_id)

        easypost_shipment.buy(rate={'id': easypost_rate.external_id})

        return easypost_shipment

    def cancel(self, easypost_rate):
        """ Allows for refunding of Rates through EasyPost
        :param rate: Unwrapped Odoo Rate record to cancel
        """

        easypost_shipment = self._get_shipment(easypost_rate)
        easypost_shipment = self.read(easypost_shipment.external_id)

        easypost_shipment.refund(rate={'id': easypost_rate.external_id})

        return easypost_shipment

    def _get_shipment(self, easypost_rate):
        """Return the binding picking and rate for an unwrapped rate."""

        easypost_rate.ensure_one()

        ship_odoo_record = self.env['easypost.shipment'].search([
            ('odoo_id', '=', easypost_rate.picking_id.id),
            ('backend_id', '=', self.backend_record.id),
        ],
            limit=1,
        )

        return ship_odoo_record
