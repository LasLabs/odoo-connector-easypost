# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock
from .common import mock_api, EasypostDeliveryHelper, mock_job_delay_to_direct


module = 'openerp.addons.connector_easypost'
job = '%s.consumer.export_record' % module
requests = '%s.models.shipping_label.requests' % module
rate = 'easypost.stock.picking.dispatch.rate'


class TestShippingLabel(EasypostDeliveryHelper):

    def setUp(self):
        super(TestShippingLabel, self).setUp(ship=True)
        self.ShipmentBuy = self.env['shipping.label.new']

    def new_rate(self, mk):
        self.rates[0]['shipment_id'] = mk.Shipment.create().id
        mk.Shipment.create().rates = self.rates
        self.delivery_id = self.env['stock.picking'].create(self.ship_vals)
        self.ep_rate_id = self.env[rate].search([
            ('easypost_id', '=', self.rates[0]['id']),
        ],
            limit=1,
        )
        return self.ep_rate_id.odoo_id

    def new_record(self, mk):
        rate_id = self.new_rate(mk)
        return self.ShipmentBuy.create({
            'rate_id': rate_id.id,
        })

    @mock.patch(requests)
    def do_test(self, req_mk):
        with mock_job_delay_to_direct(job):
            with mock_api() as mk:
                date = '2016-12-30 12:34:56'
                for i in ['label_date', 'updated_at', 'created_at']:
                    setattr(mk.Shipment.retrieve().postage_label, i, date)
                req_mk.get().content = 'Test'
                self.new_record(mk)
                return mk, req_mk

    @mock.patch(requests)
    def test_requests_called_with_label_uri(self, req_mk):
        """ It should call requests with label URI """
        mk, req_mk = self.do_test()
        req_mk.get.assert_has_calls([
            mock.call(),
            mock.call(mk.Shipment.retrieve().postage_label.label_url),
        ])

    @mock.patch(requests)
    def test_shipment_buy_reads_shipment(self, req_mk):
        """ Test that shipment purchase workflow reads external shipment """
        mk, _ = self.do_test()
        mk.Shipment.retrieve.assert_has_any_call([
            mock.call(u'%s' % self.rates[0]['shipment_id']),
        ])

    @mock.patch(requests)
    def test_shipment_buy_trigger(self, req_mk):
        """ Test shipment is purchased on easypost.shipment.buy create """
        mk, _ = self.do_test()
        mk.Shipment.retrieve().buy.assert_has_calls([
            mock.call(rate={'id': self.ep_rate_id.easypost_id}),
        ])
