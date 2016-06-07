# -*- coding: utf-8 -*-
# © 2015 LasLabs Inc.
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


class EasypostStockDeliveryRate(models.Model):
    """ Binding Model for the Easypost StockDeliveryRate """
    _name = 'easypost.stock.delivery.rate'
    _inherit = 'easypost.binding'
    _inherits = {'stock.delivery.rate': 'odoo_id'}
    _description = 'Easypost StockDeliveryRate'
    _easypost_model = 'Rate'

    odoo_id = fields.Many2one(
        comodel_name='stock.delivery.rate',
        string='StockDeliveryRate',
        required=True,
        ondelete='cascade',
    )

    _sql_constraints = [
        ('odoo_uniq', 'unique(backend_id, odoo_id)',
         'A Easypost binding for this record already exists.'),
    ]


class StockDeliveryRate(models.Model):
    """ Adds the ``one2many`` relation to the Easypost bindings
    (``easypost_bind_ids``)
    """
    _inherit = 'stock.delivery.rate'

    easypost_bind_ids = fields.One2many(
        comodel_name='easypost.stock.delivery.rate',
        inverse_name='odoo_id',
        string='Easypost Bindings',
    )


@easypost
class StockDeliveryRateAdapter(EasypostCRUDAdapter):
    """ Backend Adapter for the Easypost StockDeliveryRate """
    _model_name = 'easypost.stock.delivery.rate'


@easypost
class StockDeliveryRateImportMapper(EasypostImportMapper):
    _model_name = 'easypost.stock.delivery.rate'

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
    def group_id(self, record):
        binder = self.binder_for('easypost.easypost.shipment')
        shipment_id = binder.to_odoo(record.shipment_id, browse=True)
        return {'group_id': shipment_id.group_id.id}

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


@easypost
class StockDeliveryRateImporter(EasypostImporter):
    _model_name = ['easypost.stock.delivery.rate']
    _base_mapper = StockDeliveryRateImportMapper
