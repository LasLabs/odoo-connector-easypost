# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

"""
Helpers usable in the tests
"""
from odoo.addons.connector_easypost.connector import get_environment
from odoo.addons.connector_easypost.unit.import_synchronizer import (
    EasypostImporter,
)
from odoo.addons.connector_easypost.unit.object_dict import ObjectDict
from odoo.addons.connector_easypost.tests.common import (
    mock_api,
    SetUpEasypostBase,
)


class EasypostTrackerHelper(SetUpEasypostBase):

    def setUp(self):
        super(EasypostTrackerHelper, self).setUp()
        self.model = 'easypost.shipment.tracking.group'
        self.record = self.new_record()
        rec = self.record
        self.picking = self.create_picking(rec.shipment_id)
        self.importer = self._get_importer(self.model)
        with mock_api() as mk:
            mk.Tracker.retrieve = lambda x: rec
            self.importer.run(rec.id)

    def _get_importer(self, model):
        """ Return an EasypostImporter instance """
        env = get_environment(self.session, model,
                              self.backend_id)
        return env.get_connector_unit(EasypostImporter)

    def new_record(self):
        return ObjectDict(**{
            "id": "trk_c8e0edb5bb284caa934a0d3db23a148z",
            "object": "Tracker",
            "mode": "test",
            "tracking_code": "9400110898825022579493",
            "status": "in_transit",
            "created_at": "2016-01-13T21:52:28Z",
            "updated_at": "2016-01-13T21:52:32Z",
            "signed_by": None,
            "weight": None,
            "est_delivery_date": None,
            "shipment_id": "shp_b3740406f02c463fb29b06775e0b9c6c",
            "carrier": "USPS",
            "public_url": "https://track.easypost.com/test",
            "tracking_details": [ObjectDict(**{
                "object": "TrackingDetail",
                "message": "Shipping Label Created",
                "status": "pre_transit",
                "datetime": "2015-12-31T15:58:00Z",
                "source": "USPS",
                "tracking_location":  ObjectDict(**{
                    "object": "TrackingLocation",
                    "city": "FOUNTAIN VALLEY",
                    "state": "CA",
                    "country": "US",
                    "zip": "92708"
                })
            })],
            "carrier_detail": None,
        })

    def create_picking(self, ship_id):
        company = self.env.ref('base.main_company')
        picking_values = {
            'partner_id': self.env.ref('base.res_partner_1').id,
            'location_dest_id': self.env['stock.location'].search([])[0].id,
            'location_id': self.env['stock.location'].search([
                ('company_id', '=', company.id),
                ('name', '=', 'Stock')
            ])[0].id,
            'picking_type_id': self.env['stock.picking.type'].search([])[0].id,
        }
        picking = self.env['stock.picking'].create(picking_values)

        ep_picking_obj = self.env['easypost.shipment']
        ep_obj = ep_picking_obj.search([
            ('odoo_id', '=', picking.id),
        ])
        if not len(ep_obj):
            ep_picking_obj.create({
                'odoo_id': picking.id,
                'external_id': ship_id,
            })
        else:
            ep_obj.write({'external_id': ship_id})
        return ep_obj
