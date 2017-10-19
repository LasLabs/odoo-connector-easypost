# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from .common import EasyPostSyncTestCase, recorder


class TestImportRate(EasyPostSyncTestCase):

    def setUp(self):
        super(TestImportRate, self).setUp()
        self.model = self.env['easypost.rate']

    @recorder.use_cassette
    def test_import_rate_partner(self):
        """It should create a new delivery partner."""
        domain = [('is_carrier', '=', True)]
        self.env['res.partner'].search(domain).unlink()
        self._create_shipment()
        self.assertTrue(self.env['res.partner'].search_count(domain))

    @recorder.use_cassette
    def test_import_rate_service_new(self):
        """It should create a new delivery service."""
        domain = [('delivery_type', '=', 'easypost')]
        self.env['delivery.carrier'].search(domain).unlink()
        self._create_shipment()
        carrier_count = self.env['delivery.carrier'].search_count(domain)
        self.assertTrue(carrier_count)
        return carrier_count

    @recorder.use_cassette
    def test_import_rate_service_existing(self):
        """It should use an existing service if it matches the current."""
        existing_count = self.test_import_rate_service_new()
        self._create_shipment()
        self.assertEqual(
            existing_count,
            self.env['delivery.carrier'].search_count([
                ('delivery_type', '=', 'easypost'),
            ]),
        )
