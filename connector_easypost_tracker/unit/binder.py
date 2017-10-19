# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.connector_easypost.backend import easypost
from odoo.addons.connector_easypost.unit.binder import EasypostModelBinder


@easypost
class EasypostTrackerModelBinder(EasypostModelBinder):
    _model_name = [
        'easypost.shipment.tracking.event',
        'easypost.shipment.tracking.group',
        'easypost.shipment.tracking.location',
    ]
