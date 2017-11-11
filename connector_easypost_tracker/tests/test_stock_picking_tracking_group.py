# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import EasypostTrackerHelper


class TestStockPickingTrackingGroup(EasypostTrackerHelper):

    def test_external_id(self):
        """ It should equal the objects record_id """
        record = self.env['easypost.shipment.tracking.group'].search([
            ('external_id', '=', self.record.id)
        ])
        self.assertTrue(len(record) == 1)

    def test_ref(self):
        """ It should equal the objects tracking_code """
        record = self.env['easypost.shipment.tracking.group'].search([
            ('external_id', '=', self.record.id)
        ])
        self.assertEquals(record.ref, self.record.tracking_code)
