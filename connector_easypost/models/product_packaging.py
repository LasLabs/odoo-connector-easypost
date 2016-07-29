# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
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


class EasypostProductPackaging(models.Model):
    """ Binding Model for the Easypost ProductPackaging

        TransientModel so that records are eventually deleted due to immutable
        EasyPost objects
    """
    _name = 'easypost.product.packaging'
    _inherit = 'easypost.binding'
    _inherits = {'product.packaging': 'odoo_id'}
    _description = 'Easypost ProductPackaging'
    _easypost_model = 'Parcel'

    odoo_id = fields.Many2one(
        comodel_name='product.packaging',
        string='ProductPackaging',
        required=True,
        ondelete='cascade',
    )

    _sql_constraints = [
        ('odoo_uniq', 'unique(backend_id, odoo_id)',
         'A Easypost binding for this record already exists.'),
    ]


class ProductPackaging(models.Model):
    """ Adds the ``one2many`` relation to the Easypost bindings
    (``easypost_bind_ids``)
    """
    _inherit = 'product.packaging'

    easypost_bind_ids = fields.One2many(
        comodel_name='easypost.product.packaging',
        inverse_name='odoo_id',
        string='Easypost Bindings',
    )


@easypost
class ProductPackagingAdapter(EasypostCRUDAdapter):
    """ Backend Adapter for the Easypost ProductPackaging """
    _model_name = 'easypost.product.packaging'


@easypost
class ProductPackagingImportMapper(EasypostImportMapper):
    _model_name = 'easypost.product.packaging'

    direct = [
        (eval_false('mode'), 'mode'),
    ]

    @mapping
    @only_create
    def odoo_id(self, record):
        """ Attempt to bind on pre-existing like package """
        parcel_id = self.env['easypost.product.packaging'].search([
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
    def product_pack_tmpl_id(self, record):
        """ If being created from EasyPost for some reason, match template """
        template_id = self.env['product.packaging.template'].search([
            ('packaging_template_name', '=', record.predefined_package),
        ],
            limit=1,
        )
        if template_id:
            return {'product_pack_tmpl_id': template_id.id}

    @mapping
    @only_create
    def rows(self, record):
        """ If being created from EasyPost for some reason, map rows """
        return {'rows': 1}

    @mapping
    @only_create
    def type(self, record):
        """ If being created from EasyPost for some reason, map type """
        template_id = self.env['product.packaging.template'].search([
            ('packaging_template_name', '=', record.predefined_package),
        ],
            limit=1,
        )
        if template_id:
            return {'type': template_id.type}


@easypost
class ProductPackagingImporter(EasypostImporter):
    _model_name = ['easypost.product.packaging']
    _base_mapper = ProductPackagingImportMapper


@easypost
class ProductPackagingExportMapper(EasypostExportMapper):
    _model_name = 'easypost.product.packaging'

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
        """ Lookup the actual picking weight as the record weight
        only accounts for the weight of the packaging """
        weight = self._convert_to_ounces(
            record.weight, record.weight_uom_id,
        )
        pick = self.env['stock.picking'].search([
            ('product_packaging_id', '=', record.id)
        ])
        if len(pick):
            pick = pick[0]
            weight += self._convert_to_ounces(
                pick.weight, pick.weight_uom_id,
            )
        return {'weight': weight}


@easypost
class ProductPackagingExporter(EasypostExporter):
    _model_name = ['easypost.product.packaging']
    _base_mapper = ProductPackagingExportMapper
