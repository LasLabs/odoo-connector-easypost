# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(
        selection_add=[
            ('easypost', 'EasyPost'),
        ],
    )
    easypost_service = fields.Selection(
        string="EasyPost Carrier & Service",
        selection=[
            ('First', 'USPS - First Class'),
            ('Priority', 'USPS - Priority'),
            ('Express', 'USPS - Express'),
            ('ParcelSelect', 'USPS - Parcel Select'),
            ('LibraryMail', 'USPS - Library Mail'),
            ('MediaMail', 'USPS - Media Mail'),
            ('FirstClassMailInternational',
             'USPS - First Class Mail International'),
            ('FirstClassPackageInternationalService',
             'USPS - First Class Package International Service'),
            ('PriorityMailInternational',
             'USPS - Priority Mail International'),
            ('ExpressMailInternational',
             'USPS - Express Mail International'),
            ('Ground', 'UPS - Ground'),
            ('UPSStandard', 'UPS - UPS Standard'),
            ('UPSSaver', 'UPS - UPS Saver'),
            ('Express', 'UPS - Express'),
            ('ExpressPlus', 'UPS - Express Plus'),
            ('Expedited', 'UPS - Expedited'),
            ('NextDayAir', 'UPS - Next Day Air'),
            ('NextDayAirSaver', 'UPS - Next Day Air Saver'),
            ('NextDayAirEarlyAM', 'UPS - Next Day Air Early AM'),
            ('2ndDayAir', 'UPS - 2nd Day Air'),
            ('2ndDayAirAM', 'UPS - 2nd Day Air AM'),
            ('3DaySelect', 'UPS - 3-Day Select'),
            ('FEXEX_GROUND', 'FedEx - Ground'),
            ('FEDEX_2_DAY', 'FedEx - 2-Day'),
            ('FEDEX_2_DAY_AM', 'FedEx - 2-Day AM'),
            ('FEDEX_EXPRESS_SAVER', 'FedEx - Express Saver'),
            ('STANDARD_OVERNIGHT', 'FedEx - Standard Overnight'),
            ('FIRST_OVERNIGHT', 'FedEx - First Overnight'),
            ('PRIORITY_OVERNIGHT', 'FedEx - Priority Overnight'),
            ('INTERNATIONAL_ECONOMY', 'FedEx - International Economy'),
            ('INTERNATIONAL_FIRST', 'FedEx - International First'),
            ('INTERNATIONAL_PRIORITY', 'FedEx - International Priority'),
            ('GROUND_HOME_DELIVERY', 'FedEx - Ground Home Delivery'),
            ('SMART_POST', 'FedEx - Smart Post'),
        ],
    )

    @api.model
    def _get_shipping_label_for_rate(self, rate, wrapped=False):
        """ Returns a shipping.label for the given rate """
        easypost_label = self.env['easypost.shipping.label'].search([
            ('rate_id', '=', rate.id),
        ])
        return easypost_label if wrapped else easypost_label.odoo_id

    @api.multi
    def easypost_get_shipping_price_from_so(self, orders):
        ship_rates = []
        orders.easypost_bind_ids.ensure_bindings(orders, export=True)
        for order in orders:
            rates = order.carrier_rate_ids.filtered(
                lambda r: r.service_id == self,
            )
            if not rates:
                raise EnvironmentError(
                    _('The selected shipping service (%s) is not available '
                      'for this shipment. Please select another delivery '
                      'method') %
                    self.display_name,
                )
            ship_rates.append(rates[0].rate)
        return ship_rates

    @api.multi
    def easypost_send_shipping(self, pickings, packages=None):
        shipping_data = []
        for picking in pickings:
            rates = picking.dispatch_rate_ids.filtered(
                lambda r: self == r.service_id,
            )
            if packages:
                rates = rates.filtered(lambda r: r.package_id in packages)
            rates[0].buy()
            shipment = self._get_shipping_label_for_rate(rates[0], True)
            shipping_data.append({
                'exact_price': rates[0].rate,
                'tracking_number': shipment.tracking_number,
                'name': '%s.pdf' % shipment.tracking_number,
                'file': shipment.datas,
            })
        return shipping_data

    @api.multi
    def easypost_get_tracking_link(self, pickings):
        tracking_urls = []
        for picking in pickings:
            purchased = picking.dispatch_rate_ids.filtered(
                lambda r: r.state == 'purchase'
            )
            if purchased:
                shipment = self._get_shipping_label_for_rate(purchased, True)
                tracking_urls.append(shipment.tracking_url)
        return tracking_urls

    @api.multi
    def easypost_cancel_shipment(self, pickings):
        for picking in pickings:
            purchased = picking.dispatch_rate_ids.filtered(
                lambda r: r.state == 'purchase'
            )
            purchased.cancel()
