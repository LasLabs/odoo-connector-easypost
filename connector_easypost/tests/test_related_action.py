# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock

from openerp.addons.connector.queue.job import (Job,
                                                OpenERPJobStorage,
                                                )
from .common import mock_api, SetUpEasypostBase
from ..unit.export_synchronizer import export_record


class TestRelatedActionStorage(SetUpEasypostBase):
    """ Test related actions on stored jobs """

    def setUp(self):
        super(TestRelatedActionStorage, self).setUp()
        self.EasypostAddress = self.env['easypost.easypost.address']
        self.QueueJob = self.env['queue.job']

    def test_unwrap_binding(self):
        """ Open a related action opening an unwrapped binding """
        with mock_api():
            address_id = self.env['easypost.address'].create({
                'partner_id': self.env.user.partner_id.id,
            })
            easypost_address = self.EasypostAddress.create({
                'odoo_id': address_id.id,
                'backend_id': self.backend.id
            })
            stored = self._create_job(
                export_record, 'easypost.easypost.address',
                easypost_address.id,
            )
            expected = {
                'name': mock.ANY,
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': address_id.id,
                'res_model': 'easypost.address',
            }
            self.assertEquals(stored.open_related_action(), expected)

    def _create_job(self, func, *args):
        job = Job(func=func, args=args)
        storage = OpenERPJobStorage(self.session)
        storage.store(job)
        stored = self.QueueJob.search([('uuid', '=', job.uuid)])
        self.assertEqual(len(stored), 1)
        return stored
