# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock
from ..unit.object_dict import ObjectDict
from .common import mock_api, SetUpEasypostBase


model = 'odoo.addons.connector_easypost.models.address'


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
        self.ep_record = ObjectDict(**{
            "city": "Las Vegas",
            "country": "US",
            "created_at": "2016-12-15T22:53:39Z",
            "id": "adr_31ebaa58ce274c7084153f19441b37a3",
            "mode": "test",
            "name": "Test Customer",
            "object": "Address",
            "state": "NV",
            "street1": "123 Test St",
            "street2": "False",
            "email": "",
            "phone": "",
            "updated_at": "2016-12-15T22:53:39Z",
            "verifications": ObjectDict(**{
                "delivery": ObjectDict(**{
                    "details": {},
                    "errors": [ObjectDict(**{
                        "code": "E.ADDRESS.NOT_FOUND",
                        "field": "address",
                        "message": "Address not found",
                        "suggestion": None
                    })],
                    "success": False
                })
            }),
            "zip": "89123"
        })

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

    def test_default_partner_id(self):
        """ Test partner defaults to active partner ID """
        addr = self.Address.with_context(active_id=self.partner_id.id)
        partner = addr._default_partner_id()
        self.assertEquals(self.partner_id.id, partner)

    def test_sync_from_partner(self):
        """ Test address sync from partner correctly """
        test_street = '123 Test Drive'
        self.partner_id.write({'street': test_street})
        self.address_id._sync_from_partner()
        self.assertEquals(self.address_id.street, test_street)

    def test_action_validate(self):
        """ Test action_validate calls sync correctly """
        with mock_api():
            rec_id = self.address_id
            rec_id.partner_id._patch_method(
                '_easypost_synchronize', mock.MagicMock()
            )
            rec_id.action_validate()
            obj = rec_id.partner_id._easypost_synchronize
            # Reset the method before we assert, in case of exceptions
            rec_id.partner_id._revert_method('_easypost_synchronize')
            obj.assert_called_once_with(auto=True)


    def test_has_validation_errors(self):
        """ Test the validation errors are mapped """
        with mock_api() as mk:
            mk.Address.create = lambda **x: self.ep_record
            self._new_record()
            addr = self.EasypostAddress.search([
                ('easypost_id', '=', self.ep_record.id),
            ])
            self.assertEquals(addr.validation_errors, "Address not found")

    def test_has_validation_status(self):
        """ Test that the validation status is mapped """
        with mock_api() as mk:
            mk.Address.create = lambda **x: self.ep_record
            self._new_record()
            addr = self.EasypostAddress.search([
                ('easypost_id', '=', self.ep_record.id),
            ])
            self.assertFalse(addr.validation_status)
