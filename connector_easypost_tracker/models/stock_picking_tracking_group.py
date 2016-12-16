# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp import fields, models
from openerp.addons.connector.unit.mapper import (
    mapping,
    only_create,
)
from openerp.addons.connector_easypost.backend import easypost
from openerp.addons.connector_easypost.unit.backend_adapter import (
    EasypostCRUDAdapter,
)
from openerp.addons.connector_easypost.unit.import_synchronizer import (
    EasypostImporter,
)
from openerp.addons.connector_easypost.unit.mapper import (
    EasypostImportMapper,
    eval_false,
)
from .stock_picking_tracking_event import StockPickingTrackingEventImporter


_logger = logging.getLogger(__name__)


class EasypostStockPickingTrackingGroup(models.Model):
    """ Binding Model for the Easypost StockPickingTrackingGroup"""
    _name = 'easypost.stock.picking.tracking.group'
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

    _sql_constraints = [
        ('odoo_uniq', 'unique(backend_id, odoo_id)',
         'A Easypost binding for this record already exists.'),
    ]


class StockPickingTrackingGroup(models.Model):
    """ Adds the ``one2many`` relation to the Easypost bindings
    (``easypost_bind_ids``)
    """
    _inherit = 'stock.picking.tracking.group'

    easypost_bind_ids = fields.One2many(
        comodel_name='easypost.stock.picking.tracking.group',
        inverse_name='odoo_id',
        string='Easypost Bindings',
    )


@easypost
class EasypostStockPickingAdapter(EasypostCRUDAdapter):
    """ Backend Adapter for the Easypost EasypostStockPicking """
    _model_name = 'easypost.stock.picking.tracking.group'


@easypost
class StockPickingTrackingGroupImportMapper(EasypostImportMapper):
    _model_name = 'easypost.stock.picking.tracking.group'

    direct = [
        (eval_false('tracking_code'), 'ref'),
    ]

    @mapping
    @only_create
    def picking_id(self, record):
        pickings = self.env['easypost.stock.picking'].search([
            ('easypost_id', '=', record.shipment_id),
        ])
        if pickings:
            return {'picking_id': pickings.odoo_id.id}


@easypost
class StockPickingTrackingGroupImporter(EasypostImporter):
    _model_name = ['easypost.stock.picking.tracking.group']
    _base_mapper = StockPickingTrackingGroupImportMapper

    def _after_import(self, record):
        """ Immediately Import Events """
        importer = self.unit_for(StockPickingTrackingEventImporter,
                                 model='easypost.stock.picking.tracking.event')
        for event in self.easypost_record.tracking_details:
            event.group = record.odoo_id
            importer.easypost_record = event
            importer.run()
