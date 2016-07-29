# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock
from .common import mock_api, SetUpEasypostBase


model = 'openerp.addons.connector_easypost.models.address'


class TestAddress(SetUpEasypostBase):

    def setUp(self):
        super(TestAddress, self).setUp()
        self.EasypostAddress = self.env['easypost.easypost.address']
        self.Address = self.env['easypost.address']
        self.partner_id = self.env['res.partner'].create({
            'name': 'Test Partner',
        })
        self.address_id = self.Address.create({
            'partner_id': self.partner_id.id,
        })
        self.call_args = dict(
            city=False,
            name=u'Test Partner',
            zip=False,
            verify=['delivery'],
            street2=False,
            id=False,
            phone=False,
            state=False,
            mode=False,
            street1=False,
            country=u'US',
            email=False,
        )

    def _new_record(self):
        return self.EasypostAddress.create({
            'odoo_id': self.address_id.id,
            'backend_id': self.backend.id,
        })

    def test_get_by_partner(self):
        """ Test correct address is returned for partner via model method """
        with mock_api():
            self._new_record()
            rec_id = self.EasypostAddress._get_by_partner(
                self.partner_id,
            )
            self.assertEqual(
                self.address_id, rec_id.odoo_id,
            )

    def test_api_create_triggers_export(self):
        """ Test export of external resource on creation """
        with mock_api() as mk:
            self._new_record()
            mk.Address.create.assert_has_calls([
                mock.call(),
                mock.call(**self.call_args),
            ])

    def test_api_export_triggers_import(self):
        """ Test data is immediately imported w/ update provided by export """
        with mock_api() as mk:
            rec_id = self._new_record()
            self.assertEqual(
                u"%s" % mk.Address.create().street1, rec_id.street,
            )
