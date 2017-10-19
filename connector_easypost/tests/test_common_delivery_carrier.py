# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import EasyPostSyncTestCase, recorder


class TestDeliveryCarrier(EasyPostSyncTestCase):

    def setUp(self):
        super(TestDeliveryCarrier, self).setUp()
        self.model = self.env['delivery.carrier']

    @recorder.use_cassette
    def test_common_carrier_get_shipping_price_from_so(self):
        """It should return the proper shipping rate from the sale."""

        sale = self._create_sale()
        sale.odoo_id.action_confirm()
        shipment = sale.picking_ids[0]

        rate = shipment.dispatch_rate_ids[0]

        self.assertEqual(
            rate.service_id.easypost_get_shipping_price_from_so(sale),
            [rate.rate],
        )

    @recorder.use_cassette
    def test_common_carrier_get_shipping_label_for_rate(self):
        """It should return the shipping label for the rate."""
        rate = self._create_shipment().dispatch_rate_ids[0]
        self.assertFalse(self.model._get_shipping_label_for_rate(rate))
        rate.buy()
        self.assertTrue(self.model._get_shipping_label_for_rate(rate))
        return rate

    @recorder.use_cassette
    def test_common_carrier_send_shipping(self):
        """It should purchase the proper rate."""
        shipment = self._create_shipment()
        rate = shipment.dispatch_rate_ids[0]
        shipment_data = rate.service_id.easypost_send_shipping(shipment)
        self.assertEqual(shipment_data[0]['exact_price'], rate.rate)
        return rate

    @recorder.use_cassette
    def test_common_carrier_get_tracking_link(self):
        """It should return the tracking URLs for the rate."""
        rate = self._create_shipment().dispatch_rate_ids[0]
        method = rate.service_id.easypost_get_tracking_link
        self.assertFalse(method(rate.picking_id))
        rate.buy()
        self.assertTrue(method(rate.picking_id))

    @recorder.use_cassette
    def test_common_carrier_cancel_shipment(self):
        """It should cancel the shipment on Easypost."""
        rate = self._create_shipment().dispatch_rate_ids[0]
        rate.buy()
        self.assertFalse(rate.picking_id.easypost_bind_ids.refund_status)
        rate.cancel()
        self.assertTrue(rate.picking_id.easypost_bind_ids.refund_status)
