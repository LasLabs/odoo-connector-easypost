# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from .common import EasyPostSyncTestCase, recorder


class TestExportSale(EasyPostSyncTestCase):

    def setUp(self):
        super(TestExportSale, self).setUp()
        self.model = self.env['easypost.sale']

    @recorder.use_cassette
    def test_export_sale_imports_rates(self):
        """It should import the rates provided when the sale was exported.
        """
        sale = self._create_sale()
        self.assertTrue(sale.carrier_rate_ids)
