# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import openerp.tests.common as common
from openerp.addons.connector.session import ConnectorSession
from .common import mock_api
# from .data_base import easypost_base_responses
# from ..unit.import_synchronizer import import_record
from ..unit.export_synchronizer import export_record


backend_adapter = 'openerp.addons.connector_easypost.unit.backend_adapter'


class TestAddress(common.TransactionCase):

    def setUp(self):
        super(TestAddress, self).setUp()
        self.backend_model = self.env['easypost.backend']
        self.session = ConnectorSession(self.env.cr, self.env.uid,
                                        context=self.env.context)
        self.backend = self.backend_model.create({
            'name': 'Test Easypost',
            'version': '2',
            'api_key': 'cueqNZUb3ldeWTNX7MU3Mel8UXtaAMUi',
        })
        self.EasypostAddress = self.env['easypost.easypost.address']
        self.Address = self.env['easypost.address']
        self.address_id = self.Address.create({
            'partner_id': self.env.user.partner_id.id,
        })

    def new_record(self):
        return self.EasypostAddress.create({
            'partner_id': self.env.user.partner_id.id,
            'backend_id': self.backend.id
        })

    def test_get_by_partner(self):
        rec_id = self.Address._get_by_partner(self.env.user.partner_id)
        self.assertEqual(
            self.address_id, rec_id,
        )

    mock.patch('%s.easypost' % backend_adapter)
    def test_api_workflow_on_create(self, mk):
        """ This tests the main create/export/import cycle
        @TODO: Split these tests up
        """
        # with mock_api() as mk:
        rec_id = self.new_record()
        export_record(self.session, self.EasypostAddress._name, rec_id.id)
        mk.Address.verify.assert_called_once_with()
