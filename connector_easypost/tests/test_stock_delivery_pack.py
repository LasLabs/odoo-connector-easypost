# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import mock_api, SetUpEasypostBase
# from .data_base import easypost_base_responses
# from ..unit.import_synchronizer import import_record
# from ..unit.export_synchronizer import export_record


model = 'openerp.addons.connector_easypost.models.address'


class TestStockDeliveryPack(SetUpEasypostBase):

    def setUp(self):
        super(TestStockDeliveryPack, self).setUp()
        self.EasypostParcel = self.env['easypost.stock.delivery.pack']
        self.DeliveryPack = self.env['stock.delivery.pack']
        self.vals = {
            'length_uom_id': self.env.ref('product.product_uom_inch').id,
            'height_uom_id': self.env.ref('product.product_uom_inch').id,
            'width_uom_id': self.env.ref('product.product_uom_inch').id,
            'weight_uom_id': self.env.ref('product.product_uom_oz').id,
            'length': 1,
            'height': 2,
            'width': 3,
            'weight': 4,
            'name': 'TestPack',
            'easypost_id': 'ep_121232',
        }

    def new_record(self):
        return self.EasypostParcel.create(self.vals)

    def test_api_create_triggers_export(self):
        """ Test export of external resource on creation """
        with mock_api() as mk:
            self.new_record()
            mk.Parcel.create.assert_called_once_with(**self.vals)

    def test_api_write_triggers_export(self):
        """ Test export of external resource on creation """
        rec_id = self.new_record()
        with mock_api() as mk:
            rec_id.write({'weight': 10})
            mk.Parcel.read.assert_called_once_with(self.vals['easypost_id'])
