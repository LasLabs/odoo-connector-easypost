# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock
from .common import mock_api, mock_job_delay_to_direct, EasypostDeliveryHelper


model = 'openerp.addons.connector_easypost.models.shipment'
job = 'openerp.addons.connector_easypost.consumer.export_record'


class TestStockPicking(EasypostDeliveryHelper):

    def setUp(self):
        super(TestStockPicking, self).setUp(ship=True)
        self.DeliveryNew = self.env['stock.picking']

    def new_record(self):
        return self.DeliveryNew.create(self.ship_vals)

    def test_action_create_delivery_triggers_export(self):
        """ Test external record export on stock picking creation """
        with mock_job_delay_to_direct(job):
            with mock_api() as mk:
                mk.Shipment.create().rates = self.rates
                self.new_record()
                # @TODO: Kill multiple calls
                mk.Shipment.create.assert_has_calls([
                    mock.call(),
                    mock.call(),
                    mock.call(
                        id=False,
                        to_address={
                            'phone': u'(+886) (02) 4162 2023',
                            'state': False,
                            'name': u'ASUSTeK',
                            'zip': u'106',
                            'city': u'Taipei',
                            'street1': u'31 Hong Kong street',
                            'street2': False,
                            'country': u'TW',
                            'company': u'YourCompany',
                            'email': u'asusteK@yourcompany.example.com',
                        },
                        from_address={
                            'phone': u'+1 555 123 8069',
                            'state': u'PA',
                            'name': u'YourCompany',
                            'zip': u'18540',
                            'city': u'Scranton',
                            'street1': u'1725 Slough Ave.',
                            'street2': False,
                            'country': u'US',
                            'company': u'YourCompany',
                            'email': u'info@yourcompany.example.com',
                        },
                        parcel={'id': u"%s" % mk.Parcel.create().id},
                    )
                ])

    def test_shipment_export_triggers_package_export(self):
        """ Test that package is exported as dependency to shipment """
        with mock_job_delay_to_direct(job):
            with mock_api() as mk:
                self.new_record()
                # @TODO: Kill multiple calls
                mk.Parcel.create.assert_has_calls([
                    mock.call(),
                    mock.call(id=False, **self.ep_vals)
                ])
