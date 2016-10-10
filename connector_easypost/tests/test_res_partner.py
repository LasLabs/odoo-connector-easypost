# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock
from .common import mock_api, SetUpEasypostBase


model_path = 'openerp.addons.connector_easypost.models.res_partner'


class TestResPartner(SetUpEasypostBase):

    def setUp(self):
        super(TestResPartner, self).setUp()
        self.ResPartner = self.env['res.partner']
        self.state_id = self.env['res.country.state'].browse(1)
        self.street = '123 Street Ave'

    def new_record(self, update_vals=None):
        self.vals = {
            'name': 'Test Partner',
            'street': self.street,
            'street2': 'St 2',
            'city': 'City',
            'state_id': self.state_id.id,
            'country_id': self.state_id.country_id.id,
            'company_id': self.env.ref('base.main_company').id,
            'phone': '12341234',
            'email': 'derp@test.com',
            'zip': '89119',
        }
        if update_vals:
            self.vals.update(update_vals)
        return self.ResPartner.create(self.vals)

    def test_action_easypost_synchronize_ensure_one(self):
        with self.assertRaises(ValueError):
            self.ResPartner.search([]).action_easypost_synchronize()

    def test_action_easypost_synchronize(self):
        rec_id = self.new_record()
        context = self.env.context.copy()
        model_obj = self.env['ir.model.data']
        form_id = model_obj.xmlid_to_object(
            'connector_easypost.easypost_address_view_form',
        )
        action_id = model_obj.xmlid_to_object(
            'connector_easypost.action_easypost_address',
        )
        context.update({
            'active_id': rec_id.id,
        })
        with mock.patch.object(rec_id, '_easypost_synchronize') as mk:
            res = rec_id.action_easypost_synchronize()
            expect = {
                'name': action_id.name,
                'help': action_id.help,
                'type': action_id.type,
                'view_mode': 'form',
                'view_id': form_id.id,
                'views': [
                    (form_id.id, 'form'),
                ],
                'target': 'new',
                'context': context,
                'res_model': action_id.res_model,
                'res_id': mk()[rec_id.id].odoo_id.id,
            }
            self.assertDictEqual(
                expect, res,
            )

    def test_easypost_synchronize_new(self):
        rec_id = self.new_record()
        with mock_api():
            with mock.patch.object(rec_id, 'env') as env_mk:
                mk = env_mk['easypost.easypost.address']
                mk._get_by_partner.return_value = False
                res = rec_id._easypost_synchronize()
                mk._get_by_partner.assert_called_once_with(rec_id[0])
                mk.create.assert_called_once_with({
                    'partner_id': rec_id[0].id,
                    'backend_id': rec_id[0].company_id.easypost_backend_id.id,
                })
                self.assertEqual(
                    mk.create(), res[rec_id[0].id],
                )

    def test_easypost_synchronize_existing(self):
        rec_id = self.new_record()
        with mock_api():
            with mock.patch.object(rec_id, 'env') as env_mk:
                mk = env_mk['easypost.easypost.address']
                res = rec_id._easypost_synchronize()
                mk._get_by_partner.assert_called_once_with(rec_id[0])
                mk._get_by_partner().odoo_id.\
                    _sync_from_partner.assert_called_once_with()
                self.assertEqual(
                    mk._get_by_partner(), res[rec_id[0].id],
                )

    def test_easypost_synchronize_auto(self):
        with mock_api() as api:
            rec_id = self.new_record()
            with mock.patch.object(rec_id.env['easypost.easypost.address'],
                                   '_get_by_partner'
                                   ) as get_mk:
                get_mk.return_value = False
                rec_id._easypost_synchronize(True)
                self.assertEqual(
                    u"%s" % api.Address.create().street1, rec_id.street,
                )

    def test_easypost_synchronize_auto_company_id(self):
        with mock_api():
            rec_id = self.new_record()
            with mock.patch.object(rec_id.env['easypost.easypost.address'],
                                   '_get_by_partner'
                                   ) as get_mk:
                get_mk.return_value = False
                rec_id._easypost_synchronize(True)
                self.assertEqual(
                    self.env.ref('base.main_company'), rec_id.company_id,
                )
