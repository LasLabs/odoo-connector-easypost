# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import mock_api, mock_job_delay_to_direct, EasypostDeliveryHelper


job = 'openerp.addons.connector_easypost.consumer.export_record'
rate = 'easypost.stock.picking.dispatch.rate'


class TestStockPickingDispatchRate(EasypostDeliveryHelper):

    def setUp(self):
        super(TestStockPickingDispatchRate, self).setUp(ship=True)

    def test_shipment_export_triggers_rate_import(self):
        """ Test that rates are iterated & imported """
        with mock_job_delay_to_direct(job):
            with mock_api() as mk:
                self.rates[0]['shipment_id'] = mk.Shipment.create().id
                mk.Shipment.create().rates = self.rates
                self.env['stock.picking'].create(self.ship_vals)
                rec_id = self.env[rate].search([
                    ('easypost_id', '=', self.rates[0]['id']),
                ],
                    limit=1,
                )
                self.assertEqual(
                    self.rates[0]['rate'], rec_id.rate,
                )
