# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import EasypostTrackerHelper


class TestStockPickingTrackingEvent(EasypostTrackerHelper):

    def setUp(self):
        super(TestStockPickingTrackingEvent, self).setUp()
        group = self.env['easypost.stock.picking.tracking.group'].search([
            ('easypost_id', '=', self.record.id)
        ])
        self.event = group.last_event_id
        self.data = self.record.tracking_details[0]

    def test_message(self):
        """ It should match the event message """
        self.assertEquals(self.event.message, self.data.message)

    def test_source(self):
        """ It should match the event status """
        self.assertEquals(self.event.source, self.data.source)

    def test_state(self):
        """ It should match the event status """
        self.assertEquals(self.event.state, self.data.status)
