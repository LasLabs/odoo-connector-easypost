# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import fields, models
from odoo.addons.connector.unit.mapper import (
    mapping,
    only_create,
)
from odoo.addons.connector_easypost.backend import easypost
from odoo.addons.connector_easypost.unit.backend_adapter import (
    EasypostCRUDAdapter,
)
from odoo.addons.connector_easypost.unit.import_synchronizer import (
    EasypostImporter,
)
from odoo.addons.connector_easypost.unit.mapper import (
    EasypostImportMapper,
    eval_false,
)
from .stock_picking_tracking_event import StockPickingTrackingEventImporter


_logger = logging.getLogger(__name__)


class EasypostShipmentTrackingGroup(models.Model):
    """ Binding Model for the Easypost StockPickingTrackingGroup"""
    _name = 'easypost.shipment.tracking.group'
    _inherit = 'easypost.binding'
    _inherits = {'stock.picking.tracking.group': 'odoo_id'}
    _description = 'Easypost StockPickingTrackingGroup'
    _easypost_model = 'Tracker'

    odoo_id = fields.Many2one(
        comodel_name='stock.picking.tracking.group',
        string='Stock Picking Tracking Event',
        required=True,
        ondelete='cascade',
    )


class StockPickingTrackingGroup(models.Model):
    """ Adds the ``one2many`` relation to the Easypost bindings
    (``easypost_bind_ids``)
    """
    _inherit = 'stock.picking.tracking.group'

    easypost_bind_ids = fields.One2many(
        comodel_name='easypost.shipment.tracking.group',
        inverse_name='odoo_id',
        string='Easypost Bindings',
    )


@easypost
class EasypostShipmentAdapter(EasypostCRUDAdapter):
    """ Backend Adapter for the Easypost EasypostShipment """
    _model_name = 'easypost.shipment.tracking.group'


@easypost
class StockPickingTrackingGroupImportMapper(EasypostImportMapper):
    _model_name = 'easypost.shipment.tracking.group'

    direct = [
        (eval_false('tracking_code'), 'ref'),
    ]

    @mapping
    @only_create
    def picking_id(self, record):
        pickings = self.env['easypost.shipment'].search([
            ('external_id', '=', record.shipment_id),
        ])
        if pickings:
            return {'picking_id': pickings.odoo_id.id}


@easypost
class StockPickingTrackingGroupImporter(EasypostImporter):
    _model_name = ['easypost.shipment.tracking.group']
    _base_mapper = StockPickingTrackingGroupImportMapper

    def _after_import(self, record):
        """ Immediately Import Events """
        importer = self.unit_for(StockPickingTrackingEventImporter,
                                 model='easypost.shipment.tracking.event')
        for event in self.easypost_record.tracking_details:
            event.group = record.odoo_id
            importer.easypost_record = event
            importer.run()
