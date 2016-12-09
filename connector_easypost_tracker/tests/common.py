# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

"""
Helpers usable in the tests
"""
from openerp.addons.connector_easypost.tests.common import (
    SetUpEasypostBase,
    ObjDict,
)


class EasypostTrackerHelper(SetUpEasypostBase):

    def new_record(self):
        return ObjDict(**{
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
            "shipment_id": None,
            "carrier": "USPS",
            "public_url": "https://track.easypost.com/test",
            "tracking_details": [{
                "object": "TrackingDetail",
                "message": "Shipping Label Created",
                "status": "pre_transit",
                "datetime": "2015-12-31T15:58:00Z",
                "source": "USPS",
                "tracking_location": {
                    "object": "TrackingLocation",
                    "city": "FOUNTAIN VALLEY",
                    "state": "CA",
                    "country": None,
                    "zip": "92708"
                }
            }],
            "carrier_detail": None,
        })
