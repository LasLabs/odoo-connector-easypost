# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp import models, fields
from openerp.addons.connector.unit.mapper import (mapping,
                                                  changed_by,
                                                  )
from ..unit.backend_adapter import EasypostCRUDAdapter
from ..unit.mapper import (EasypostImportMapper,
                           EasypostExportMapper,
                           )
from ..backend import easypost
from ..unit.import_synchronizer import (EasypostImporter)
from ..unit.export_synchronizer import (EasypostExporter)


_logger = logging.getLogger(__name__)


class EasypostStockQuantPackage(models.Model):
    """ Binding Model for the Easypost StockQuantPackage

        TransientModel so that records are eventually deleted due to immutable
        EasyPost objects
    """
    _name = 'easypost.stock.quant.package'
    _inherit = 'easypost.binding'
    _inherits = {'stock.quant.package': 'odoo_id'}
    _description = 'Easypost StockQuantPackage'
    _easypost_model = 'Parcel'

    odoo_id = fields.Many2one(
        comodel_name='stock.quant.package',
        string='StockQuantPackage',
        required=True,
        ondelete='cascade',
    )

    _sql_constraints = [
        ('odoo_uniq', 'unique(backend_id, odoo_id)',
         'A Easypost binding for this record already exists.'),
    ]


class StockQuantPackage(models.Model):
    """ Adds the ``one2many`` relation to the Easypost bindings
    (``easypost_bind_ids``)
    """
    _inherit = 'stock.quant.package'

    easypost_bind_ids = fields.One2many(
        comodel_name='easypost.stock.quant.package',
        inverse_name='odoo_id',
        string='Easypost Bindings',
    )


@easypost
class StockQuantPackageAdapter(EasypostCRUDAdapter):
    """ Backend Adapter for the Easypost StockQuantPackage """
    _model_name = 'easypost.stock.quant.package'


@easypost
class StockQuantPackageImportMapper(EasypostImportMapper):
    _model_name = 'easypost.stock.quant.package'


@easypost
class StockQuantPackageImporter(EasypostImporter):
    _model_name = ['easypost.stock.quant.package']
    _base_mapper = StockQuantPackageImportMapper


@easypost
class StockQuantPackageExportMapper(EasypostExportMapper):
    _model_name = 'easypost.stock.quant.package'

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
    @changed_by('product_pack_tmpl_id.length',
                'product_pack_tmpl_id.length_uom_id')
    def length(self, record):
        length = self._convert_to_inches(
            record.product_pack_tmpl_id.length,
            record.product_pack_tmpl_id.length_uom_id,
        )
        return {'length': length}

    @mapping
    @changed_by('product_pack_tmpl_id.width',
                'product_pack_tmpl_id.width_uom_id')
    def width(self, record):
        width = self._convert_to_inches(
            record.product_pack_tmpl_id.width,
            record.product_pack_tmpl_id.width_uom_id,
        )
        return {'width': width}

    @mapping
    @changed_by('product_pack_tmpl_id.height',
                'product_pack_tmpl_id.height_uom_id')
    def height(self, record):
        height = self._convert_to_inches(
            record.product_pack_tmpl_id.height,
            record.product_pack_tmpl_id.height_uom_id,
        )
        return {'height': height}

    @mapping
    @changed_by('total_weight', 'product_pack_tmpl_id.weight_uom_id')
    def weight(self, record):
        """ Lookup the actual picking weight as the record weight
        only accounts for the weight of the packaging """
        weight = self._convert_to_ounces(
            record.product_pack_tmpl_id.weight + record.total_weight,
            record.product_pack_tmpl_id.weight_uom_id,
        )
        return {'weight': weight}


@easypost
class StockQuantPackageExporter(EasypostExporter):
    _model_name = ['easypost.stock.quant.package']
    _base_mapper = StockQuantPackageExportMapper
