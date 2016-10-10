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
from ..unit.mapper import eval_false
from .stock_picking_dispatch_rate import StockPickingDispatchRateImporter
from .shipping_label import ShippingLabelImporter


_logger = logging.getLogger(__name__)


class EasypostStockPicking(models.Model):
    """ Binding Model for the Easypost EasypostStockPicking """
    _name = 'easypost.stock.picking'
    _inherit = 'easypost.binding'
    _inherits = {'stock.picking': 'odoo_id'}
    _description = 'Easypost EasypostStockPicking'
    _easypost_model = 'Shipment'

    odoo_id = fields.Many2one(
        comodel_name='stock.picking',
        string='StockPicking',
        required=True,
        ondelete='cascade',
    )

    _sql_constraints = [
        ('odoo_uniq', 'unique(backend_id, odoo_id)',
         'A Easypost binding for this record already exists.'),
    ]


class StockPicking(models.Model):
    """ Adds the ``one2many`` relation to the Easypost bindings
    (``easypost_bind_ids``)
    """
    _inherit = 'stock.picking'

    product_packaging_id = fields.Many2one(
        string='Delivery Packaging',
        comodel_name='product.packaging',
    )
    easypost_bind_ids = fields.One2many(
        comodel_name='easypost.stock.picking',
        inverse_name='odoo_id',
        string='Easypost Bindings',
    )


@easypost
class EasypostStockPickingAdapter(EasypostCRUDAdapter):
    """ Backend Adapter for the Easypost EasypostStockPicking """
    _model_name = 'easypost.stock.picking'

    def buy(self, rate_record):
        """ Allows for purchasing of Shipments through EasyPost
        :param rate_record: Unwrapped Odoo Rate record to purchase label for
        """
        rate_id = rate_record.picking_id.easypost_bind_ids.id
        ship_odoo_record = self.env['easypost.stock.picking'].search([
            ('easypost_bind_ids', '=', rate_id),
        ],
            limit=1,
        )
        rate_record = self.env['easypost.stock.picking.dispatch.rate'].search([
            ('odoo_id', '=', rate_record.easypost_bind_ids.odoo_id.id),
        ],
            limit=1,
        )
        _logger.debug('Purchasing shipment %s with rate %s',
                      ship_odoo_record.easypost_id, rate_record.easypost_id)
        ship_easypost_record = self.read(ship_odoo_record.easypost_id)
        ship_easypost_record.buy(rate={'id': rate_record.easypost_id})

        label_importer = self.unit_for(ShippingLabelImporter,
                                       model='easypost.shipping.label')
        label_importer.easypost_record = ship_easypost_record
        label_importer.run(ship_easypost_record.id)

        return ship_easypost_record


@easypost
class EasypostStockPickingImportMapper(EasypostImportMapper):
    _model_name = 'easypost.stock.picking'

    direct = [
        (eval_false('mode'), 'mode'),
    ]

    @mapping
    def rates(self, record):
        importer = self.unit_for(StockPickingDispatchRateImporter,
                                 model='easypost.stock.picking.dispatch.rate')
        for rate in record.rates:
            importer.run(rate.id)


@easypost
class EasypostStockPickingImporter(EasypostImporter):
    _model_name = ['easypost.stock.picking']
    _base_mapper = EasypostStockPickingImportMapper

    def _is_uptodate(self, binding):
        """Return False to always force import """
        return False


@easypost
class EasypostStockPickingExportMapper(EasypostExportMapper):
    _model_name = 'easypost.stock.picking'

    def _map_partner(self, partner_id):
        """ @TODO: Figure out how to use the real importer here """
        vals = {
            'name': partner_id.name,
            'street1': partner_id.street,
            'street2': partner_id.street2,
            'email': partner_id.email,
            'phone': partner_id.phone,
            'city': partner_id.city,
            'zip': partner_id.zip,
            'state': partner_id.state_id.code,
            'country': partner_id.country_id.code,
        }
        if partner_id.company_id:
            vals['company'] = partner_id.company_id.name
        return vals

    @mapping
    @changed_by('product_packaging_id')
    def parcel(self, record):
        binder = self.binder_for('easypost.product.packaging')
        parcel = binder.to_backend(record.product_packaging_id)
        return {'parcel': {'id': parcel}}

    @mapping
    @changed_by('partner_id')
    def to_address(self, record):
        return {'to_address': self._map_partner(record.partner_id)}

    @mapping
    @changed_by('location_id')
    def from_address(self, record):
        loc_id_int = record.location_id.id
        warehouse_id = self.env['stock.warehouse'].search([
            ('lot_stock_id', 'parent_of', loc_id_int),
        ],
            limit=1,
        )
        return {'from_address': self._map_partner(warehouse_id.partner_id)}


@easypost
class EasypostStockPickingExporter(EasypostExporter):
    _model_name = ['easypost.stock.picking']
    _base_mapper = EasypostStockPickingExportMapper

    def _export_dependencies(self):
        _logger.debug('Exporting Dependency %r',
                      self.binding_record.product_packaging_id)
        self._export_dependency(self.binding_record.product_packaging_id,
                                'easypost.product.packaging')

    def _after_export(self):
        """ Immediate re-import """
        importer = self.unit_for(StockPickingDispatchRateImporter,
                                 model='easypost.stock.picking.dispatch.rate')
        for rate in self.easypost_record.rates:
            rate['easypost_bind_ids'] = self.binding_record.id
            importer.easypost_record = rate
            importer.run(rate.id)
