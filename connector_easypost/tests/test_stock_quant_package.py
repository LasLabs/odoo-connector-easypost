# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock
from .common import mock_api, mock_job_delay_to_direct, EasypostDeliveryHelper


model = 'openerp.addons.connector_easypost.models.address'
job = 'openerp.addons.connector_easypost.consumer.export_record'


class TestStockQuantPackage(EasypostDeliveryHelper):

    def setUp(self):
        super(TestStockQuantPackage, self).setUp()
        self.Parcel = self.env['stock.quant.package']
        self.converted = {
            'length': .4,
            'width': 1.19,
            'height': .79,
            'weight': .15,
        }
        self.pack_tpl_id = self.create_product_packaging_template()
        self.vals = {'product_pack_tmpl_id': self.pack_tpl_id.id}

    def _convert_uom(self, name):
        if name == 'weight':
            uom_id = self.oz_id.id
        else:
            uom_id = self.inch_id.id
        self.pack_vals.update({
            '%s_uom_id' % name: uom_id,
            name: self.converted[name],
        })
        self.ep_vals.update({
            name: self.converted[name],
        })

    def new_record(self):
        return self.Parcel.create(self.vals)

    def test_api_create_triggers_export(self):
        """ Test export of external resource on creation """
        with mock_job_delay_to_direct(job):
            with mock_api() as mk:
                self.new_record()
                mk.Parcel.create.assert_has_calls([
                    mock.call(),
                    mock.call(id=False,
                              **self.ep_vals),
                ])

    def test_api_write_triggers_export(self):
        """ Test export of external resource on write """
        with mock_job_delay_to_direct(job):
            with mock_api() as mk:
                self.new_record()
                args = mk.Parcel.create.call_args
                expect = mock.call(id=False,
                                   **self.ep_vals)
                self.assertEqual(
                    expect, args,
                )

    def _uom_conversion_helper(self, name, uom_id):
        self.pack_vals['%s_uom_id' % name] = uom_id.id
        with mock_job_delay_to_direct(job):
            with mock_api() as mk:
                pack = self.create_product_packaging_template()
                self.vals['product_pack_tmpl_id'] = pack.id
                self.new_record()
                self._convert_uom(name)
                mk.Parcel.create.assert_has_calls([
                    mock.call(),
                    mock.call(id=False, **self.ep_vals),
                ])

    def test_export_length_convert(self):
        self._uom_conversion_helper('length', self.cm_id)

    def test_export_width_convert(self):
        self._uom_conversion_helper('width', self.cm_id)

    def test_export_height_convert(self):
        self._uom_conversion_helper('height', self.cm_id)

    def test_export_weight_convert(self):
        self._uom_conversion_helper('weight', self.gram_id)
