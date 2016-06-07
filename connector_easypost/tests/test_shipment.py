# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock
from .common import mock_api, mock_job_delay_to_direct, SetUpEasypostBase


model = 'openerp.addons.connector_easypost.models.shipment'
job = 'openerp.addons.connector_easypost.consumer.export_record'


class ObjDict(dict):
    def __getattr__(self, key):
        try:
            return super(ObjDict, self).__getattr__(key)
        except AttributeError:
            return self[key]


class TestShipment(SetUpEasypostBase):

    def setUp(self):
        super(TestShipment, self).setUp()
        self.DeliveryPack = self.env['stock.delivery.pack']
        self.DeliveryNew = self.env['stock.delivery.new']
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
        self.converted = {
            'length': .4,
            'width': 1.19,
            'height': .79,
            'weight': .15,
        }
        self.pack_vals = {
            'length_uom_id': self.inch_id.id,
            'height_uom_id': self.inch_id.id,
            'width_uom_id': self.inch_id.id,
            'weight_uom_id': self.oz_id.id,
            'name': 'TestPack',
        }
        self.pack_vals.update(self.ep_vals)
        self.pack_tpl_id = self.env['stock.delivery.pack.template'].create(
            self.pack_vals
        )
        self.quant_pack_id = self.env['stock.quant.package'].create({})
        pack_vals = {'pack_template_id': self.pack_tpl_id.id,
                     'quant_pack_id': self.quant_pack_id.id,
                     }
        pack_vals.update(self.pack_vals)
        self.pack_id = self.env['stock.delivery.pack'].create(pack_vals)
        self.picking_id = self.env['stock.picking'].create({
            'location_dest_id': self.env['stock.location'].search([])[0].id,
            'location_id': self.env['stock.location'].search([])[0].id,
            'picking_type_id':
                self.env['stock.picking.type'].search([])[0].id,
        })
        self.group_id = self.env['stock.delivery.group'].create({
            'picking_id': self.picking_id.id,
            'pack_id': self.pack_id.id,
        })
        self.rates = [
            ObjDict(**{
                "carrier": "USPS",
                "carrier_account_id": "ca_ac8c059614f5495295d1161dfa1f0290",
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
                "shipment_id": "shp_62e87c088fba4532b80288222771b4fc",
                "updated_at": "2016-06-07 03:25:48",
            }),
        ]

    def new_record(self):
        return self.DeliveryNew.create({
            'quant_pack_id': self.quant_pack_id.id,
            'delivery_pack_id': self.pack_id.id,
            'pack_operation_ids': [(4, 1)],
        })

    def test_action_create_delivery_triggers_export(self):
        """ Test external record export on action_create_delivery """
        with mock_job_delay_to_direct(job):
            with mock_api() as mk:
                self.new_record().action_create_delivery()
                # @TODO: Kill multiple calls
                mk.Shipment.create.assert_has_calls([
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
                self.new_record().action_create_delivery()
                # @TODO: Kill multiple calls
                mk.Parcel.create.assert_has_calls([
                    mock.call(),
                    mock.call(id=False, **self.ep_vals)
                ])

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
