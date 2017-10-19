# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from .common import EasyPostSyncTestCase


class TestCommonResCompany(EasyPostSyncTestCase):

    def setUp(self):
        super(TestCommonResCompany, self).setUp()
        self.model = self.env['res.company']
        self.record = self.env.user.company_id

    def test_compute_easypost_backend_id(self):
        """It should have the backend as the default for the company."""
        self.assertEqual(self.record.easypost_backend_id, self.backend)
