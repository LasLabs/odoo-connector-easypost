# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.connector_easypost.unit.object_dict import ObjectDict
from .common import EasypostTrackerHelper


class TestStockPickingTrackingLocation(EasypostTrackerHelper):

    _location_model = 'easypost.shipment.tracking.location'

    def setUp(self):
        super(TestStockPickingTrackingLocation, self).setUp()
        group = self.env['easypost.shipment.tracking.group'].search([
            ('external_id', '=', self.record.id)
        ])
        self.location = group.location_id
        self.data = self.record.tracking_details[0].tracking_location

    def test_city(self):
        """ It should match the event city """
        self.assertEquals(self.location.city, self.data.city)

    def test_zip(self):
        """ It should match the location zip """
        self.assertEquals(self.location.zip, self.data.zip)

    def test_state_id(self):
        """ It should match the location state """
        self.assertEquals(self.location.state_id.code, self.data.state)

    def test_location_id(self):
        """ It should match the location state """
        self.assertEquals(self.location.state_id.country_id.code,
                          self.data.country)

    def test_default_easypost_values(self):
        """ It should use default values from the origin location to
        map missing but required values from the location object """
        broken_data = ObjectDict(**{
            "city": "",
            "state": "",
            "zip": ""
        })
        importer = self._get_importer(self._location_model)
        importer.easypost_record = broken_data
        importer.default_easypost_values(
            self.picking.company_id
        )
        expected_vals = {
            'city': self.picking.company_id.city,
            'state': self.picking.company_id.state_id.code,
            'zip': self.picking.company_id.zip,
        }
        actual_vals = {
            'city': importer.easypost_record.city,
            'state': importer.easypost_record.state,
            'zip': importer.easypost_record.zip,
        }
        self.assertEqual(expected_vals, actual_vals)

    def test_default_id(self):
        """ It should equal the hex digest of the MD5 hash of the city,
        state and zip of the location object """
        expected = u"loc_c10e6da33abcab202dab527c3f1a7f7e"
        test_data = ObjectDict(**{
            "city": "Las Vegas",
            "state": "NV",
            "zip": "89183",
            "country": None,
        })
        importer = self._get_importer(self._location_model)
        importer.easypost_record = test_data
        actual = importer.run()
        self.assertEquals(actual.external_id, expected)
