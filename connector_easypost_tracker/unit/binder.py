# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.connector_easypost.backend import easypost
from odoo.addons.connector_easypost.unit.binder import EasypostModelBinder


@easypost
class EasypostTrackerModelBinder(EasypostModelBinder):
    _model_name = [
        'easypost.stock.picking.tracking.event',
        'easypost.stock.picking.tracking.group',
        'easypost.stock.picking.tracking.location',
    ]
