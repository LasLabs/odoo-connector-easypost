# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from .common import EasyPostSyncTestCase, recorder


class TestExportParcel(EasyPostSyncTestCase):

    def setUp(self):
        super(TestExportParcel, self).setUp()
        self.model = self.env['easypost.parcel']

    @recorder.use_cassette
    def test_export_parcel_predefined_package(self):
        """It should pass the predefined package information when applicable.
        """
        parcel = self._create_parcel()
        external = self._get_external(parcel.external_id)
        self.assertEqual(external.predefined_package,
                         self.record.packaging_id.shipper_package_code)

    @recorder.use_cassette
    def test_export_parcel_shipping_weight(self):
        """It should export the parcel using shipping weight when avail."""
        parcel = self._create_parcel()
        external = self._get_external(parcel.external_id)
        self.assertTrue(external)
        self.assertEqual(external.weight, self.record.shipping_weight)

    @recorder.use_cassette
    def test_export_parcel_total_weight(self):
        """It should export the parcel using calculated weight when no manual.
        """
        vals = {'quant_ids': [(6, 0, self._create_quant().ids)],
                'shipping_weight': False}
        parcel = self._create_parcel(vals=vals)
        external = self._get_external(parcel.external_id)
        self.assertTrue(external)
        self.assertEqual(external.weight, self.record.total_weight)
