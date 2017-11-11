# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from .common import EasyPostSyncTestCase, recorder


class TestCommonRate(EasyPostSyncTestCase):

    @recorder.use_cassette
    def test_rate_buy(self):
        """It should purchase the rate."""
        shipment = self._create_shipment()
        self.assertFalse(shipment.shipping_label_ids)
        shipment.dispatch_rate_ids[0].buy()
        self.assertTrue(shipment.shipping_label_ids)
        return shipment

    @recorder.use_cassette
    def test_rate_cancel(self):
        """It should cancel the rate."""
        shipment = self.test_rate_buy()
        self.assertFalse(shipment.refund_status)
        shipment.dispatch_rate_ids[0].cancel()
        self.assertTrue(shipment.refund_status)
