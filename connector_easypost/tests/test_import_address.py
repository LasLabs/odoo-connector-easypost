# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from .common import EasyPostSyncTestCase, recorder


class TestImportAddress(EasyPostSyncTestCase):

    def setUp(self):
        super(TestImportAddress, self).setUp()
        self.model = self.env['easypost.address']
        self.partner = self._create_partner()
        self.record = self.model.create({
            'partner_id': self.partner.id,
        })
        self.validated = {
            'street': u'1600 PENNSYLVANIA AVE NW',
            'street2': False,
            'city': u'WASHINGTON',
            'state_id': self.env.ref('base.state_us_9').id,
            'zip': u'20500-0003',
            'country_id': self.env.ref('base.us').id,
            'is_valid': True,
            'latitude': 38.8987,
            'longitude': -77.0352,
            'validation_messages':
                u'Missing secondary information(Apt/Suite#)',
        }

    @recorder.use_cassette
    def test_backend_easypost_get_address(self):
        """It should return the validated address."""
        res = self.backend.easypost_get_address(self.partner)
        self.assertDictEqual(res, self.validated)
