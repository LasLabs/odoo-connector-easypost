# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)

try:
    from openerp.addons.connector_easypost.backend import easypost
    from openerp.addons.connector_easypost.unit.binder import (
        EasypostModelBinder
    )
except ImportError:
    _logger.warning('Could not import dependencies from `connector_easypost`')


@easypost
class EasypostTrackerModelBinder(EasypostModelBinder):
    _model_name = [
        # 'easypost.stock.picking.tracking.event',
        'easypost.stock.picking.tracking.group',
        # 'easypost.stock.picking.tracking.location',
    ]
