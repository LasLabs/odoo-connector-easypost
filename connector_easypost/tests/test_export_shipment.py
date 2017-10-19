# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from .common import EasyPostSyncTestCase, recorder


class TestExportShipment(EasyPostSyncTestCase):

    def setUp(self):
        super(TestExportShipment, self).setUp()
        self.model = self.env['easypost.shipment']

    @recorder.use_cassette
    def test_export_shipment_basic(self):
        """It should perform a basic shipment export."""
        shipment = self._create_shipment()
        self.assertTrue(self._get_external(shipment.external_id))

    @recorder.use_cassette
    def test_export_shipment_imports_rates(self):
        """It should import the rates provided when the shipment was exported.
        """
        shipment = self._create_shipment(export=False)
        self.assertFalse(shipment.dispatch_rate_ids)
        shipment.export_record()
        self.assertTrue(shipment.dispatch_rate_ids)
