# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import mock_api, mock_job_delay_to_direct, EasypostDeliveryHelper


job = 'openerp.addons.connector_easypost.consumer.export_record'


class TestStockDeliveryRate(EasypostDeliveryHelper):

    def setUp(self):
        super(TestStockDeliveryRate, self).setUp(ship=True)
        self.DeliveryNew = self.env['stock.delivery.new']

    def new_record(self):
        return self.DeliveryNew.create({
            'quant_pack_id': self.quant_pack_id.id,
            'delivery_pack_id': self.pack_id.id,
            'pack_operation_ids': [(4, 1)],
        })

    def test_shipment_export_triggers_rate_import(self):
        """ Test that rates are iterated & imported """
        with mock_job_delay_to_direct(job):
            with mock_api() as mk:
                self.rates[0]['shipment_id'] = mk.Shipment.create().id
                mk.Shipment.create().rates = self.rates
                self.new_record().action_create_delivery()
                rec_id = self.env['easypost.stock.delivery.rate'].search([
                    ('easypost_id', '=', self.rates[0]['id']),
                ],
                    limit=1,
                )
                self.assertEqual(
                    self.rates[0]['rate'], rec_id.rate,
                )
