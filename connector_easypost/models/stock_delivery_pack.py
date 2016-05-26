# -*- coding: utf-8 -*-
# © 2015 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp import models, fields, api
from openerp.addons.connector.connector import ConnectorUnit
from openerp.addons.connector.unit.mapper import (mapping,
                                                  changed_by,
                                                  only_create,
                                                  ExportMapper,
                                                  )
from ..unit.backend_adapter import EasypostCRUDAdapter
from ..unit.mapper import (EasypostImportMapper,
                           )
# from ..connector import get_environment
from ..backend import easypost
from ..unit.import_synchronizer import (DelayedBatchImporter,
                                        EasypostImporter,
                                        )
from ..unit.export_synchronizer import (EasypostExporter)
from ..connector import add_checkpoint
from ..unit.mapper import eval_false


_logger = logging.getLogger(__name__)


class EasypostStockDeliveryPack(models.TransientModel):
    """ Binding Model for the Easypost StockDeliveryPack

        TransientModel so that records are eventually deleted due to immutable
        EasyPost objects
    """
    _name = 'easypost.stock.delivery.pack'
    _inherit = 'easypost.binding'
    _inherits = {'stock.delivery.pack': 'odoo_id'}
    _description = 'Easypost StockDeliveryPack'
    _easypost_model = 'Parcel'

    odoo_id = fields.Many2one(
        comodel_name='stock.delivery.pack',
        string='StockDeliveryPack',
        required=True,
        ondelete='cascade',
    )
    backend_id = fields.Many2one(
        comodel_name='easypost.backend',
        string='Easypost Backend',
        store=True,
        readonly=True,
    )

    _sql_constraints = [
        ('odoo_uniq', 'unique(backend_id, odoo_id)',
         'A Easypost binding for this patient already exists.'),
    ]


class StockDeliveryPack(models.TransientModel):
    """ Adds the ``one2many`` relation to the Easypost bindings
    (``easypost_bind_ids``)
    """
    _inherit = 'stock.delivery.pack'

    easypost_bind_ids = fields.One2many(
        comodel_name='easypost.stock.delivery.pack',
        inverse_name='odoo_id',
        string='Easypost Bindings',
    )


@easypost
class StockDeliveryPackAdapter(EasypostCRUDAdapter):
    """ Backend Adapter for the Easypost StockDeliveryPack """
    _model_name = 'easypost.stock.delivery.pack'

    def read(self, _id):
        """ Gets record by id and returns the object
        :param _id: Id of record to get from Db
        :type _id: int
        :return: EasyPost record for model
        """
        return self._get_ep_model().verify(id=_id)


@easypost
class StockDeliveryPackBatchImporter(DelayedBatchImporter):
    """ Import the Easypost StockDeliveryPacks.
    For every patient in the list, a delayed job is created.
    """
    _model_name = ['easypost.stock.delivery.pack']

    def run(self, filters=None):
        """ Run the synchronization """
        if filters is None:
            filters = {}
        record_ids = self.backend_adapter.search(**filters)
        for record_id in record_ids:
            self._import_record(record_id)


@easypost
class StockDeliveryPackImportMapper(EasypostImportMapper):
    _model_name = 'easypost.stock.delivery.pack'

    direct = [
        (eval_false('mode'), 'mode'),
    ]

    @mapping
    @only_create
    def length_uom_id(self, record):
        """ If being created from EasyPost for some reason, add inches UOM """
        return {'length_uom_id': self.env.ref('product.product_uom_inch').id}

    @mapping
    @only_create
    def width_uom_id(self, record):
        """ If being created from EasyPost for some reason, add inches UOM """
        return {'width_uom_id': self.env.ref('product.product_uom_inch').id}

    @mapping
    @only_create
    def height_uom_id(self, record):
        """ If being created from EasyPost for some reason, add inches UOM """
        return {'height_uom_id': self.env.ref('product.product_uom_inch').id}

    @mapping
    @only_create
    def weight_uom_id(self, record):
        """ If being created from EasyPost for some reason, add oz UOM """
        return {'weight_uom_id': self.env.ref('product.product_uom_oz').id}

    @mapping
    @only_create
    def length(self, record):
        """ If being created from EasyPost for some reason, return in inches """
        return {'length': record.length}

    @mapping
    @only_create
    def width(self, record):
        """ If being created from EasyPost for some reason, return in inches """
        return {'width': record.width}

    @mapping
    @only_create
    def height(self, record):
        """ If being created from EasyPost for some reason, return in inches """
        return {'height': record.height}

    @mapping
    @only_create
    def weight(self, record):
        """ If being created from EasyPost for some reason, return in inches """
        return {'weight': record.weight}

    @mapping
    @only_create
    def name(self, record):
        """ If being created from EasyPost for some reason, map name """
        return {'name': record.predefined_package}

    @mapping
    @only_create
    def pack_template_id(self, record):
        """ If being created from EasyPost for some reason, match template """
        template_id = self.env['stock.delivery.pack.template'].search([
            ('name', '=', record.predefined_package),
        ],
            limit=1,
        )
        if template_id:
            return {'pack_template_id': template_id.id}


@easypost
class StockDeliveryPackImporter(EasypostImporter):
    _model_name = ['easypost.stock.delivery.pack']

    _base_mapper = StockDeliveryPackImportMapper

    def _create(self, data):
        binding = super(StockDeliveryPackImporter, self)._create(data)
        checkpoint = self.unit_for(StockDeliveryPackAddCheckpoint)
        checkpoint.run(binding.id)
        return binding


@easypost
class StockDeliveryPackExportMapper(ExportMapper):
    _model_name = 'easypost.stock.delivery.pack'

    def _convert_to_inches(self, uom_qty, uom_id):
        inches_id = self.env.ref('product.product_uom_inch')
        if uom_id.id != inches_id.id:
            return uom_id._compute_qty_obj(uom_qty, inches_id)
        else:
            return uom_qty

    def _convert_to_ounces(self, uom_qty, uom_id):
        oz_id = self.env.ref('product.product_uom_oz')
        if uom_id.id != oz_id.id:
            return uom_id._compute_qty_obj(uom_qty, oz_id)
        else:
            return uom_qty

    @mapping
    @changed_by('length', 'length_uom_id')
    def length(self, record):
        length = self._convert_to_inches(
            record.length, record.length_uom_id,
        )
        return {'length': length}

    @mapping
    @changed_by('width', 'width_uom_id')
    def width(self, record):
        width = self._convert_to_inches(
            record.width, record.width_uom_id,
        )
        return {'width': width}

    @mapping
    @changed_by('height', 'height_uom_id')
    def height(self, record):
        length = self._convert_to_inches(
            record.height, record.height_uom_id,
        )
        return {'height': height}

    @mapping
    @changed_by('weight', 'weight_uom_id')
    def weight(self, record):
        length = self._convert_to_ounces(
            record.weight, record.weight_uom_id,
        )
        return {'weight': weight}

    @mapping
    def id(self, record):
        return {'id': record.easypost_id}


@easypost
class StockDeliveryPackExporter(EasypostExporter):
    _model_name = ['easypost.stock.delivery.pack']
    _base_mapper = StockDeliveryPackExportMapper

    def _after_export(self):
        binding = self.binding_record.with_context(connector_no_export=True)
        importer = self.unit_for(StockDeliveryPackImporter)
        map_record = importer.mapper.map_record(self.easypost_id)
        update_vals = map_record.values()
        _logger.debug('Writing to %s with %s',
                      self.binding_record, update_vals)
        binding.write(update_vals)


@easypost
class StockDeliveryPackAddCheckpoint(ConnectorUnit):
    """ Add a connector.checkpoint on the easypost.stock.delivery.pack record """
    _model_name = ['easypost.stock.delivery.pack', ]

    def run(self, binding_id):
        add_checkpoint(self.session,
                       self.model._name,
                       binding_id,
                       self.backend_record.id)
