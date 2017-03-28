# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock
from .common import mock_api, mock_job_delay_to_direct, EasypostDeliveryHelper


module = 'odoo.addons.connector_easypost'
job = '%s.consumer.export_record' % module
requests = '%s.models.shipping_label.requests' % module


class TestDeliveryCarrier(EasypostDeliveryHelper):

    def setUp(self):
        super(TestDeliveryCarrier, self).setUp(ship=True)

    def new_rate(self, mk):
        self.rates[0]['shipment_id'] = mk.Shipment.create().id
        mk.Shipment.create().rates = self.rates
        self.delivery_id = self.create_picking()
        self.ep_rate_id = self.env['easypost.stock.picking.rate'].search([
            ('easypost_id', '=', self.rates[0]['id']),
        ],
            limit=1,
        )
        return self.ep_rate_id.odoo_id

    @mock.patch(requests)
    def do_test(self, req_mk):
        with mock_job_delay_to_direct(job):
            with mock_api() as mk:
                date = '2016-12-30 12:34:56'
                for i in ['label_date', 'updated_at', 'created_at']:
                    setattr(mk.Shipment.retrieve().postage_label, i, date)
                mk.Shipment.retrieve().selected_rate.id = self.rates[0]['id']
                mk.Shipment.retrieve().tracker.public_url = 'http://TRK123'
                req_mk.get().content = 'Test'
                rate_id = self.new_rate(mk)
                rate_id.buy()
                return mk, req_mk

    def _create_delivery_carrier(self):
        return self.env['delivery.carrier'].create({
            'name': 'Test',
            'delivery_type': 'easypost',
            'easypost_service': 'First',
        })

    @mock.patch(requests)
    def test_easypost_cancel_shipment(self, req_mk):
        """ Test shipment is canceled on easypost.shipment.cancel """
        with mock_api() as mk:
            req_mk.get().content = 'Test'
            self.do_test()
            self.ep_rate_id.state = 'cancel'
            mk.Shipment.retrieve().refund.assert_has_calls([
                mock.call(rate={'id': self.ep_rate_id.easypost_id}),
            ])

    def test_get_shipment_for_rate(self):
        self.do_test()
        label = self._create_delivery_carrier()._get_shipment_for_rate(
            self.ep_rate_id.odoo_id
        )
        self.assertEquals(label.rate_id, self.ep_rate_id.odoo_id)

    def test_easypost_get_shipping_price_from_so(self):
        """ It should return the correct rate for the given SO """
        with mock_job_delay_to_direct(job):
            with mock_api() as mk:
                mk.Shipment.retrieve().selected_rate.id = self.rates[0]['id']
                self.new_rate(mk)
                self.env['stock.picking']._patch_method(
                    'search',
                    mock.MagicMock(return_value=self.delivery_id)
                )
                carrier = self._create_delivery_carrier()
                prices = []
                try:
                    prices = carrier.easypost_get_shipping_price_from_so(
                        [self.env.ref('sale.sale_order_1')]
                    )
                except Exception:
                    self.env['stock.picking']._revert_method('search')
                    raise
                self.env['stock.picking']._revert_method('search')
            self.assertIn(36.18, prices)

    @mock.patch(requests)
    def test_easypost_send_shipping(self, req_mk):
        """ It should call .buy() on the chosen rate """
        with mock_job_delay_to_direct(job):
            with mock_api() as mk:
                mk.Shipment.retrieve().selected_rate.id = self.rates[0]['id']
                rate = self.new_rate(mk)
                carrier = self._create_delivery_carrier()
                date = '2016-12-30 12:34:56'
                for i in ['label_date', 'updated_at', 'created_at']:
                    setattr(mk.Shipment.retrieve().postage_label, i, date)
                mk.Shipment.retrieve().selected_rate.id = self.rates[0]['id']
                req_mk.get().content = 'Test'
                carrier.easypost_send_shipping(self.delivery_id)
                self.assertEquals(rate.state, 'purchase')

    def test_easypost_open_tracking_page(self):
        """ It should contain the tracking URL """
        mk, req_mk = self.do_test()
        tu = self.env['delivery.carrier'].easypost_open_tracking_page([
            self.delivery_id
        ])
        self.assertIn('http://TRK123', tu)
