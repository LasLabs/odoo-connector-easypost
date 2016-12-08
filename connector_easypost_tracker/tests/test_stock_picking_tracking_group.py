# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp.addons.connector_easypost.unit.import_synchronizer import (
    import_record,
)
from openerp.addons.connector_easypost.tests.common import mock_api
from .common import EasypostTrackerHelper


_logger = logging.getLogger(__name__)


class TestStockPickingTrackingGroup(EasypostTrackerHelper):

    def setUp(self):
        super(TestStockPickingTrackingGroup, self).setUp()
        self.model = 'easypost.stock.picking.tracking.group'
        self.record = self.new_record()
        self._import_record()

    def _import_record(self):
        rec = self.record
        with mock_api() as mk:
            mk.Tracker.retrieve = lambda x: rec
            import_record(self.session, self.model, self.backend_id, rec.id)

    def test_easypost_id(self):
        """ It should equal the objects record_id """
        record = self.env['easypost.stock.picking.tracking.group'].search([
            ('easypost_id', '=', self.record.id)
        ])
        self.assertTrue(len(record) == 1)

    def test_ref(self):
        """ It should equal the objects tracking_code """
        record = self.env['easypost.stock.picking.tracking.group'].search([
            ('easypost_id', '=', self.record.id)
        ])
        self.assertEquals(record.ref, self.record.tracking_code)
