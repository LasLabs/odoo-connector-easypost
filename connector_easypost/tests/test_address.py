# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import mock_api, SetUpEasypostBase
# from .data_base import easypost_base_responses
# from ..unit.import_synchronizer import import_record
# from ..unit.export_synchronizer import export_record


model = 'openerp.addons.connector_easypost.models.address'


class TestAddress(SetUpEasypostBase):

    def setUp(self):
        super(TestAddress, self).setUp()
        self.EasypostAddress = self.env['easypost.easypost.address']
        self.Address = self.env['easypost.address']
        self.address_id = self.Address.create({
            'partner_id': self.env.user.partner_id.id,
        })
        self.call_args = dict(
            city=False,
            name=u'Administrator',
            zip=False,
            street1=False,
            street2=False,
            id=False,
            phone=False,
            state=False,
            mode=False,
            verify=['delivery'],
            country=u'US',
            company=u'YourCompany',
            email=u'admin@yourcompany.example.com',
        )

    def new_record(self):
        return self.EasypostAddress.create({
            'partner_id': self.env.user.partner_id.id,
            'backend_id': self.backend.id
        })

    def test_get_by_partner(self):
        """ Test correct address is returned for partner via model method """
        rec_id = self.Address._get_by_partner(self.env.user.partner_id)
        self.assertEqual(
            self.address_id, rec_id,
        )

    def test_api_create_triggers_export(self):
        """ Test export of external resource on creation """
        with mock_api() as mk:
            self.new_record()
            mk.Address.create.assert_called_once_with(**self.call_args)

    def test_api_export_triggers_import(self):
        """ Test data is immediately imported w/ update provided by export """
        with mock_api() as mk:
            expect = '123 Street Street'
            mk.Address.create().street1 = expect
            rec_id = self.new_record()
            self.assertEqual(
                expect, rec_id.street,
            )
