# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

"""
Helpers usable in the tests
"""

import importlib
import mock
from contextlib import contextmanager
import openerp.tests.common as common
from openerp.addons.connector.session import ConnectorSession


backend_adapter = 'openerp.addons.connector_easypost.unit.backend_adapter'
inc_id = 0
asustek_partner_id = 'res_partner_1'
your_company_id = 'main_company'


@contextmanager
def mock_job_delay_to_direct(job_path):
    """ Replace the .delay() of a job by a direct call
    job_path is the python path, such as::
      openerp.addons.easypost.stock_picking.export_picking_done
    """
    job_module, job_name = job_path.rsplit('.', 1)
    module = importlib.import_module(job_module)
    job_func = getattr(module, job_name, None)
    assert job_func, "The function %s must exist in %s" % (job_name,
                                                           job_module)

    def clean_args_for_func(*args, **kwargs):
        # remove the special args reserved to .delay()
        kwargs.pop('priority', None)
        kwargs.pop('eta', None)
        kwargs.pop('model_name', None)
        kwargs.pop('max_retries', None)
        kwargs.pop('description', None)
        job_func(*args, **kwargs)

    with mock.patch(job_path) as patched_job:
        # call the direct export instead of 'delay()'
        patched_job.delay.side_effect = clean_args_for_func
        yield patched_job


@contextmanager
def mock_api(models=None, actions=None, ret_val=False):
    """ Mock the Easypost API """
    global inc_id
    if models is None:
        models = ['Address', 'Parcel', 'Shipment', 'Rate']
    if actions is None:
        actions = ['create', 'retrieve']
    with mock.patch('%s.easypost' % backend_adapter) as API:
        for model in models:
            model = getattr(API, model)
            for action in actions:
                if action == 'create':
                    inc_id += 1
                action = getattr(model, action)()
                for col in ['created_at', 'updated_at']:
                    setattr(action, col, ret_val)
                setattr(action, 'id', inc_id)
                setattr(action, 'mode', '__TEST__')
        yield API


class EasypostHelper(object):

    def __init__(self, cr, registry, model_name):
        self.cr = cr
        self.model = registry(model_name)


class ObjDict(dict):

    def __getattr__(self, key):
        try:
            return super(ObjDict, self).__getattr__(key)
        except AttributeError:
            return self[key]


class SetUpEasypostBase(common.TransactionCase):
    """ Base class - Test the imports from a Easypost Mock.
    The data returned by Easypost are those created for the
    demo version of Easypost on a standard 2 version.
    """

    def setUp(self):
        super(SetUpEasypostBase, self).setUp()
        self.backend_model = self.env['easypost.backend']
        self.session = ConnectorSession(
            self.env.cr, self.env.uid, context=self.env.context,
        )
        self.backend = self.get_easypost_backend()
        self.backend_id = self.backend.id

    def get_easypost_backend(self):
        domain = [
            ('company_id', '=', self.env.ref('base.main_company').id),
            ('is_default', '=', True),
        ]
        backends = self.backend_model.search(domain)
        if len(backends) > 0:
            return backends[0]
        else:
            return self.backend_model.create({
                'name': 'Test Easypost',
                'version': '2',
                'api_key': 'cueqNZUb3ldeWTNX7MU3Mel8UXtaAMUi',
            })

    def get_easypost_helper(self, model_name):
        return EasypostHelper(self.cr, self.registry, model_name)


class EasypostDeliveryHelper(SetUpEasypostBase):

    def setUp(self, ship=False):
        super(EasypostDeliveryHelper, self).setUp()
        self.pack_cnt = 0
        self.cm_id = self.env.ref('product.product_uom_cm')
        self.inch_id = self.env.ref('product.product_uom_inch')
        self.oz_id = self.env.ref('product.product_uom_oz')
        self.gram_id = self.env.ref('product.product_uom_gram')
        self.ep_vals = {
            'length': 1.0,
            'height': 2.0,
            'width': 3.0,
            'weight': 4.0,
        }
        self.pack_vals = {
            'length_uom_id': self.inch_id.id,
            'height_uom_id': self.inch_id.id,
            'width_uom_id': self.inch_id.id,
            'weight_uom_id': self.oz_id.id,
            'package_type': 'box',
            'packaging_template_name': 'TestPackTpl',
        }
        self.pack_vals.update(self.ep_vals)
        if ship:
            company = self.env.ref('base.%s' % your_company_id)
            product = self.env.ref('product.product_product_6')
            self.pack_tpl_id = self.create_product_packaging_template()
            self.ship_vals = {
                'partner_id': self.env.ref('base.%s' % asustek_partner_id).id,
                'location_dest_id': self.env['stock.location'].search([
                    ])[0].id,
                'location_id': self.env['stock.location'].search([
                    ('company_id', '=', company.id),
                    ('name', '=', 'Stock')
                ])[0].id,
                'picking_type_id':
                    self.env['stock.picking.type'].search([])[0].id,
                'move_lines': [[0, False, {
                    'name': product.name,
                    'product_id': product.id,
                    'product_uom': product.uom_id.id,
                    'product_uom_qty': '1',
                    'state': 'draft'
                }]]
            }
            self.rates = [
                ObjDict(**{
                    "carrier": "USPS",
                    "carrier_account_id":
                        "ca_ac8c059614f5495295d1161dfa1f0290",
                    "created_at": "2016-06-07 03:25:48",
                    "currency": "USD",
                    "delivery_date": None,
                    "delivery_date_guaranteed": None,
                    "delivery_days": 1,
                    "est_delivery_days": 1,
                    "id": "rate_912d3f794ded45a9b0963d44d0cccbb7",
                    "list_currency": "USD",
                    "list_rate": 36.18,
                    "mode": "test",
                    "object": "Rate",
                    "rate": 36.18,
                    "retail_currency": None,
                    "retail_rate": None,
                    "service": "Express",
                    "shipment_id":
                        "shp_62e87c088fba4532b80288222771b4fc",
                    "updated_at": "2016-06-07 03:25:48",
                }),
            ]

    def create_picking(self):
        picking = self.env['stock.picking'].create(self.ship_vals)
        picking.action_confirm()
        picking.force_assign()
        for item in picking.pack_operation_product_ids:
            item.qty_done = 1.0
        picking.put_in_pack()
        for item in picking.pack_operation_ids.result_package_id:
            item.product_pack_tmpl_id = self.pack_tpl_id.id
        return picking

    def create_product_packaging_template(self):
        self.pack_vals['packaging_template_name'] = '%s_%s' % (
            self.pack_vals['packaging_template_name'],
            self.pack_cnt
        )
        self.pack_cnt += 1
        return self.env['product.packaging.template'].create(
            self.pack_vals
        )
