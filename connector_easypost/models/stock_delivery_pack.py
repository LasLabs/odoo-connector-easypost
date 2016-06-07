# -*- coding: utf-8 -*-
# © 2015 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp import models, fields
from openerp.addons.connector.unit.mapper import (mapping,
                                                  changed_by,
                                                  only_create,
                                                  )
from ..unit.backend_adapter import EasypostCRUDAdapter
from ..unit.mapper import (EasypostImportMapper,
                           EasypostExportMapper,
                           )
from ..backend import easypost
from ..unit.import_synchronizer import (EasypostImporter)
from ..unit.export_synchronizer import (EasypostExporter)
from ..unit.mapper import eval_false


_logger = logging.getLogger(__name__)


class EasypostStockDeliveryPack(models.Model):
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

    _sql_constraints = [
        ('odoo_uniq', 'unique(backend_id, odoo_id)',
         'A Easypost binding for this record already exists.'),
    ]


class StockDeliveryPack(models.Model):
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


@easypost
class StockDeliveryPackImportMapper(EasypostImportMapper):
    _model_name = 'easypost.stock.delivery.pack'

    direct = [
        (eval_false('mode'), 'mode'),
    ]

    @mapping
    @only_create
    def odoo_id(self, record):
        """ Attempt to bind on pre-existing like package """
        parcel_id = self.env['easypost.stock.delivery.pack'].search([
            ('easypost_id', '=', record.id),
            ('backend_id', '=', self.backend_record.id),
        ],
            limit=1,
        )
        if parcel_id:
            return {'odoo_id': parcel_id.odoo_id.id}

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
        """ If being created from EasyPost for some reason, return in inch """
        return {'length': record.length}

    @mapping
    @only_create
    def width(self, record):
        """ If being created from EasyPost for some reason, return in inch """
        return {'width': record.width}

    @mapping
    @only_create
    def height(self, record):
        """ If being created from EasyPost for some reason, return in inch """
        return {'height': record.height}

    @mapping
    @only_create
    def weight(self, record):
        """ If being created from EasyPost for some reason, return in inch """
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


@easypost
class StockDeliveryPackExportMapper(EasypostExportMapper):
    _model_name = 'easypost.stock.delivery.pack'

    def _convert_to_inches(self, uom_qty, uom_id):
        inches_id = self.env.ref('product.product_uom_inch')
        if uom_id.id != inches_id.id:
            return self.env['product.uom']._compute_qty_obj(
                uom_id, uom_qty, inches_id,
            )
        else:
            return uom_qty

    def _convert_to_ounces(self, uom_qty, uom_id):
        oz_id = self.env.ref('product.product_uom_oz')
        if uom_id.id != oz_id.id:
            return self.env['product.uom']._compute_qty_obj(
                uom_id, uom_qty, oz_id,
            )
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
        height = self._convert_to_inches(
            record.height, record.height_uom_id,
        )
        return {'height': height}

    @mapping
    @changed_by('weight', 'weight_uom_id')
    def weight(self, record):
        weight = self._convert_to_ounces(
            record.weight, record.weight_uom_id,
        )
        return {'weight': weight}


@easypost
class StockDeliveryPackExporter(EasypostExporter):
    _model_name = ['easypost.stock.delivery.pack']
    _base_mapper = StockDeliveryPackExportMapper
