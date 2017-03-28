# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(
        selection_add=[
            ('auto', 'Automatic'),
            ('easypost', 'EasyPost'),
        ],
    )
    easypost_service = fields.Selection(
        string="EasyPost Carrier & Service",
        selection=[
            ('First', 'USPS - First'),
            ('Priority', 'USPS - Priority'),
            ('Express', 'USPS - Express'),
            ('ParcelSelect', 'USPS - ParcelSelect'),
            ('LibraryMail', 'USPS - LibraryMail'),
            ('MediaMail', 'USPS - MediaMail'),
            ('FirstClassMailInternational',
             'USPS - FirstClassMailInternational'),
            ('FirstClassPackageInternationalService',
             'USPS - FirstClassPackageInternationalService'),
            ('PriorityMailInternational', 'USPS - PriorityMailInternational'),
            ('ExpressMailInternational', 'USPS - ExpressMailInternational'),
            ('Ground', 'UPS - Ground'),
            ('UPSStandard', 'UPS - UPSStandard'),
            ('UPSSaver', 'UPS - UPSSaver'),
            ('Express', 'UPS - Express'),
            ('ExpressPlus', 'UPS - ExpressPlus'),
            ('Expedited', 'UPS - Expedited'),
            ('NextDayAir', 'UPS - NextDayAir'),
            ('NextDayAirSaver', 'UPS - NextDayAirSaver'),
            ('NextDayAirEarlyAM', 'UPS - NextDayAirEarlyAM'),
            ('2ndDayAir', 'UPS - 2ndDayAir'),
            ('2ndDayAirAM', 'UPS - 2ndDayAirAM'),
            ('3DaySelect', 'UPS - 3DaySelect'),
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

    def _get_shipment_for_rate(self, rate):
        """ Returns a shipping.label for the given rate """
        return self.env['shipping.label'].search([
            ('rate_id', '=', rate.id),
        ])

    def easypost_get_shipping_price_from_so(self, orders):
        ship_rates = []
        for order in orders:
            picking = self.env['stock.picking'].search([
                ('sale_id', '=', order.id),
            ])
            for rate in picking.dispatch_rate_ids:
                if self.easypost_service == rate.service_id.name:
                    ship_rates.append(rate.rate)
                else:
                    raise EnvironmentError(
                        _('Service %s not found in EasyPost' %
                          self.easypost_service)
                    )
        return ship_rates

    def easypost_send_shipping(self, pickings):
        shipping_data = []
        for picking in pickings:
            for rate in picking.dispatch_rate_ids:
                if self.easypost_service == rate.service_id.name:
                    rate.buy()
                    shipment = self._get_shipment_for_rate(rate)
                    shipping_data.append({
                        'exact_price': rate.rate,
                        'tracking_number': shipment.tracking_number,

                    })
        return shipping_data

    def easypost_open_tracking_page(self, pickings):
        tracking_urls = []
        for picking in pickings:
            purchased = picking.dispatch_rate_ids.filtered(
                lambda r: r.state == 'purchase'
            )
            if purchased:
                shipment = self._get_shipment_for_rate(purchased)
                tracking_urls.append(shipment.tracking_url)
        return tracking_urls

    def easypost_cancel_shipment(self, pickings):
        for picking in pickings:
            purchased = picking.dispatch_rate_ids.filtered(
                lambda r: r.state == 'purchase'
            )
            if purchased:
                purchased.state = 'cancel'
