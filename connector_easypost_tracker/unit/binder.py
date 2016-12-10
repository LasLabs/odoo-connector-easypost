# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.connector_easypost.backend import easypost
from openerp.addons.connector_easypost.unit.binder import EasypostModelBinder


@easypost
class EasypostTrackerModelBinder(EasypostModelBinder):
    _model_name = [
        'easypost.stock.picking.tracking.group',
    ]
