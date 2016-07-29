# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
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


class EasypostShippingLabel(models.Model):
    """ Binding Model for the Easypost ShippingLabel """
    _name = 'easypost.shipping.label'
    _inherit = 'easypost.binding'
    _inherits = {'shipping.label': 'odoo_id'}
    _description = 'Easypost ShippingLabel'
    _easypost_model = 'Shipment'

    odoo_id = fields.Many2one(
        comodel_name='shipping.label',
        string='ShippingLabel',
        required=True,
        ondelete='cascade',
    )

    _sql_constraints = [
        ('odoo_uniq', 'unique(backend_id, odoo_id)',
         'A Easypost binding for this record already exists.'),
    ]


class ShippingLabel(models.Model):
    """ Adds the ``one2many`` relation to the Easypost bindings
    (``easypost_bind_ids``)
    """
    _inherit = 'shipping.label'

    easypost_bind_ids = fields.One2many(
        comodel_name='easypost.shipping.label',
        inverse_name='odoo_id',
        string='Easypost Bindings',
    )
    rate_id = fields.Many2one(
        string='Rate',
        comodel_name='stock.picking.dispatch.rate',
    )


@easypost
class ShippingLabelAdapter(EasypostCRUDAdapter):
    """ Backend Adapter for the Easypost ShippingLabel """
    _model_name = 'easypost.shipping.label'


@easypost
class ShippingLabelImportMapper(ImportMapper):
    _model_name = 'easypost.shipping.label'

    direct = [
        (inner_attr('postage_label', 'id'), 'easypost_id'),
    ]

    @mapping
    @only_create
    def datas(self, record):
        label = requests.get(record.postage_label.label_url)
        return {'datas': label.content.encode('base64')}

    @mapping
    @only_create
    def rate_id(self, record):
        binder = self.binder_for('easypost.stock.picking.dispatch.rate')
        rate_id = binder.to_odoo(record.selected_rate.id)
        return {'rate_id': rate_id}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @mapping
    def name(self, record):
        return {'name': record.postage_label.label_url.split('/')[-1]}


@easypost
class ShippingLabelImporter(EasypostImporter):
    _model_name = ['easypost.shipping.label']
    _base_mapper = ShippingLabelImportMapper
