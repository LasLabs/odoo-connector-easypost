# -*- coding: utf-8 -*-
# © 2015 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import requests
from openerp import models, fields
from openerp.addons.connector.unit.mapper import (mapping,
                                                  only_create,
                                                  ImportMapper,
                                                  )
from ..unit.backend_adapter import EasypostCRUDAdapter
from ..backend import easypost
from ..unit.import_synchronizer import (EasypostImporter)
from ..unit.mapper import inner_attr


_logger = logging.getLogger(__name__)


class EasypostStockDeliveryLabel(models.Model):
    """ Binding Model for the Easypost StockDeliveryLabel """
    _name = 'easypost.stock.delivery.label'
    _inherit = 'easypost.binding'
    _inherits = {'stock.delivery.label': 'odoo_id'}
    _description = 'Easypost StockDeliveryLabel'
    _easypost_model = 'Shipment'

    odoo_id = fields.Many2one(
        comodel_name='stock.delivery.label',
        string='StockDeliveryLabel',
        required=True,
        ondelete='cascade',
    )

    _sql_constraints = [
        ('odoo_uniq', 'unique(backend_id, odoo_id)',
         'A Easypost binding for this record already exists.'),
    ]


class StockDeliveryLabel(models.Model):
    """ Adds the ``one2many`` relation to the Easypost bindings
    (``easypost_bind_ids``)
    """
    _inherit = 'stock.delivery.label'

    easypost_bind_ids = fields.One2many(
        comodel_name='easypost.stock.delivery.label',
        inverse_name='odoo_id',
        string='Easypost Bindings',
    )


@easypost
class StockDeliveryLabelAdapter(EasypostCRUDAdapter):
    """ Backend Adapter for the Easypost StockDeliveryLabel """
    _model_name = 'easypost.stock.delivery.label'


@easypost
class StockDeliveryLabelImportMapper(ImportMapper):
    _model_name = 'easypost.stock.delivery.label'

    direct = [
        (inner_attr('postage_label', 'created_at'), 'created_at'),
        (inner_attr('postage_label', 'updated_at'), 'updated_at'),
        (inner_attr('postage_label', 'id'), 'easypost_id'),
        (inner_attr('postage_label', 'label_date'), 'date_generated'),
    ]

    @mapping
    @only_create
    def img_label(self, record):
        label = requests.get(record.postage_label.label_url)
        return {'img_label': label.content.encode('base64')}

    @mapping
    @only_create
    def rate_id(self, record):
        binder = self.binder_for('easypost.stock.delivery.rate')
        rate_id = binder.to_odoo(record.selected_rate.id)
        return {'rate_id': rate_id}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}


@easypost
class StockDeliveryLabelImporter(EasypostImporter):
    _model_name = ['easypost.stock.delivery.label']
    _base_mapper = StockDeliveryLabelImportMapper
