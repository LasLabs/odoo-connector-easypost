# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock
from .common import mock_api, mock_job_delay_to_direct, EasypostDeliveryHelper


model = 'openerp.addons.connector_easypost.models.address'
job = 'openerp.addons.connector_easypost.consumer.export_record'


class TestStockDeliveryPack(EasypostDeliveryHelper):

    def setUp(self):
        super(TestStockDeliveryPack, self).setUp()
        self.EasypostParcel = self.env['easypost.product.packaging']
        self.vals = self.pack_vals
        self.converted = {
            'length': .4,
            'width': 1.19,
            'height': .79,
            'weight': .15,
        }
        self.vals.update(self.ep_vals)

    def _convert_uom(self, name):
        if name == 'weight':
            uom_id = self.oz_id.id
        else:
            uom_id = self.inch_id.id
        self.vals.update({
            '%s_uom_id' % name: uom_id,
            name: self.converted[name],
        })
        self.ep_vals.update({
            name: self.converted[name],
        })

    def new_record(self):
        return self.EasypostParcel.create(self.vals)

    def test_api_create_triggers_export(self):
        """ Test export of external resource on creation """
        with mock_job_delay_to_direct(job):
            with mock_api() as mk:
                self.new_record()
                mk.Parcel.create.assert_has_calls([
                    mock.call(),
                    mock.call(id=False, **self.ep_vals),
                ])

    def test_api_write_triggers_export(self):
        """ Test export of external resource on write """
        rec_id = self.new_record()
        with mock_job_delay_to_direct(job):
            with mock_api() as mk:
                self.ep_vals.update({'weight': 10.0})
                rec_id.write(self.ep_vals)
                args = mk.Parcel.create.call_args
                expect = mock.call(id=False,
                                   **self.ep_vals)
                self.assertEqual(
                    expect, args,
                    'Did not call create w/ args on write. '
                    'Expect %s, Got %s' % (
                        expect, args,
                    )
                )

    def _uom_conversion_helper(self, name, uom_id):
        self.vals['%s_uom_id' % name] = uom_id.id
        with mock_job_delay_to_direct(job):
            with mock_api() as mk:
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
