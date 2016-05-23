# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock

import openerp
import openerp.tests.common as common
from openerp.addons.connector.queue.job import (Job,
                                                OpenERPJobStorage,
                                                )
from openerp.addons.connector.session import ConnectorSession
from .common import mock_api
from .data_base import easypost_base_responses
from ..unit.import_synchronizer import import_batch, import_record
from ..unit.export_synchronizer import export_record


class TestRelatedActionStorage(common.TransactionCase):
    """ Test related actions on stored jobs """

    def setUp(self):
        super(TestRelatedActionStorage, self).setUp()
        self.backend_model = self.env['easypost.backend']
        self.session = ConnectorSession(self.env.cr, self.env.uid,
                                        context=self.env.context)
        # warehouse = self.env.ref('stock.warehouse0')
        self.backend = self.backend_model.create({
            'name': 'Test Easypost',
            'version': '2',
            'api_key': 'cueqNZUb3ldeWTNX7MU3Mel8UXtaAMUi',
        })
        # import the base informations
        with mock_api(easypost_base_responses):
            import_batch(
                self.session, 'easypost.medical.pharmacy', self.backend.id
            )
        self.EasypostProduct = self.env['easypost.product.product']
        self.QueueJob = self.env['queue.job']

    def test_unwrap_binding(self):
        """ Open a related action opening an unwrapped binding """
        product = self.env.ref('product.product_product_7')
        easypost_product = self.EasypostProduct.create(
            {'openerp_id': product.id,
             'backend_id': self.backend.id})
        stored = self._create_job(export_record, 'easypost.product.product',
                                  easypost_product.id)
        expected = {
            'name': mock.ANY,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': product.id,
            'res_model': 'product.product',
        }
        self.assertEquals(stored.open_related_action(), expected)

    def _create_job(self, func, *args):
        job = Job(func=func, args=args)
        storage = OpenERPJobStorage(self.session)
        storage.store(job)
        stored = self.QueueJob.search([('uuid', '=', job.uuid)])
        self.assertEqual(len(stored), 1)
        return stored

    def test_link(self):
        """ Open a related action opening an url on Easypost """
        self.backend.write({'admin_location': 'http://www.example.com/admin'})
        stored = self._create_job(import_record, 'easypost.product.product',
                                  self.backend.id, 123456)
        url = 'http://www.example.com/admin/catalog_product/edit/id/123456'
        expected = {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': url,
        }
        self.assertEquals(stored.open_related_action(), expected)

    def test_link_no_location(self):
        """ Related action opening an url, admin location is not configured """
        self.backend.write({'admin_location': False})
        self.backend.refresh()
        stored = self._create_job(import_record, 'easypost.product.product',
                                  self.backend.id, 123456)
        with self.assertRaises(openerp.exceptions.Warning):
            stored.open_related_action()
