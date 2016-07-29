# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import re
from openerp import models, fields
from openerp.addons.connector.unit.mapper import (mapping,
                                                  only_create,
                                                  )
from ..unit.backend_adapter import EasypostCRUDAdapter
from ..unit.mapper import (EasypostImportMapper)
from ..backend import easypost
from ..unit.import_synchronizer import (EasypostImporter)
from ..unit.mapper import eval_false

_logger = logging.getLogger(__name__)


class EasypostStockPickingDispatchRate(models.Model):
    """ Binding Model for the Easypost StockPickingDispatchRate """
    _name = 'easypost.stock.picking.dispatch.rate'
    _inherit = 'easypost.binding'
    _inherits = {'stock.picking.dispatch.rate': 'odoo_id'}
    _description = 'Easypost StockPickingDispatchRate'
    _easypost_model = 'Rate'

    odoo_id = fields.Many2one(
        comodel_name='stock.picking.dispatch.rate',
        string='StockPickingDispatchRate',
        required=True,
        ondelete='cascade',
    )

    _sql_constraints = [
        ('odoo_uniq', 'unique(backend_id, odoo_id)',
         'A Easypost binding for this record already exists.'),
    ]


class StockPickingDispatchRate(models.Model):
    """ Adds the ``one2many`` relation to the Easypost bindings
    (``easypost_bind_ids``)
    """
    _inherit = 'stock.picking.dispatch.rate'

    easypost_bind_ids = fields.One2many(
        comodel_name='easypost.stock.picking.dispatch.rate',
        inverse_name='odoo_id',
        string='Easypost Bindings',
    )


@easypost
class StockPickingDispatchRateAdapter(EasypostCRUDAdapter):
    """ Backend Adapter for the Easypost StockPickingDispatchRate """
    _model_name = 'easypost.stock.picking.dispatch.rate'


@easypost
class StockPickingDispatchRateImportMapper(EasypostImportMapper):
    _model_name = 'easypost.stock.picking.dispatch.rate'

    direct = [
        (eval_false('mode'), 'mode'),
        (eval_false('rate'), 'rate'),
        (eval_false('list_rate'), 'list_rate'),
        (eval_false('retail_rate'), 'retail_rate'),
        (eval_false('delivery_days'), 'delivery_days'),
        (eval_false('delivery_date_guaranteed'), 'is_guaranteed'),
        (eval_false('delivery_date'), 'date_delivery'),
    ]

    def _camel_to_title(self, camel_case):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_case)
        return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)

    def _get_currency_id(self, name):
        return self.env['res.currency'].search([
            ('name', '=', name),
        ],
            limit=1,
        )

    @mapping
    @only_create
    def rate_currency_id(self, record):
        return {'rate_currency_id': self._get_currency_id(record.currency).id}

    @mapping
    @only_create
    def retail_rate_currency_id(self, record):
        return {
            'retail_rate_currency_id':
                self._get_currency_id(record.retail_currency).id,
        }

    @mapping
    @only_create
    def list_rate_currency_id(self, record):
        return {
            'list_rate_currency_id':
                self._get_currency_id(record.list_currency).id,
        }

    @mapping
    @only_create
    def service_id(self, record):
        service_obj = self.env['delivery.carrier']
        partner_obj = self.env['res.partner']
        partner_id = partner_obj.search([
            ('name', '=', record.carrier),
            ('is_carrier', '=', True),
        ],
            limit=1,
        )
        if not partner_id:
            partner_id = partner_obj.create({
                'name': record.carrier,
                'is_carrier': True,
                'customer': False,
                'supplier': False,
            })
        service_id = service_obj.search([
            ('partner_id', '=', partner_id.id),
            ('name', '=', record.service),
            ('delivery_type', '=', 'auto'),
        ],
            limit=1,
        )
        if not service_id:
            service_id = service_obj.create({
                'name': record.service,
                'display_name': self._camel_to_title(record.service),
                'partner_id': partner_id.id,
                'delivery_type': 'auto',
            })
        return {'service_id': service_id.id}

    @mapping
    @only_create
    def picking_id(self, record):
        picking = self.env['stock.picking'].search([
            ('easypost_bind_ids', '=', record.easypost_bind_ids)
        ],
            limit=1,
        )
        return {'picking_id': picking.id}


@easypost
class StockPickingDispatchRateImporter(EasypostImporter):
    _model_name = ['easypost.stock.picking.dispatch.rate']
    _base_mapper = StockPickingDispatchRateImportMapper
