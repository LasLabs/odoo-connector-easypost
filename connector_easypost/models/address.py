# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp import models, fields, api
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


class EasypostEasypostAddress(models.TransientModel):
    """ Binding Model for the Easypost EasypostAddress

        TransientModel so that records are eventually deleted due to immutable
        EasyPost objects
    """
    _name = 'easypost.easypost.address'
    _inherit = 'easypost.binding'
    _inherits = {'easypost.address': 'odoo_id'}
    _description = 'Easypost EasypostAddress'
    _easypost_model = 'Address'

    odoo_id = fields.Many2one(
        comodel_name='easypost.address',
        string='EasypostAddress',
        required=True,
        ondelete='cascade',
    )

    _sql_constraints = [
        ('odoo_uniq', 'unique(backend_id, odoo_id)',
         'A Easypost binding for this record already exists.'),
    ]

    @api.model
    def _get_by_partner(self, partner_id):
        return self.search([
            ('partner_id', '=', partner_id.id),
        ],
            limit=1,
        )


class EasypostAddress(models.TransientModel):
    """ Adds the ``one2many`` relation to the Easypost bindings
    (``easypost_bind_ids``)
    """
    _inherit = 'easypost.address'

    easypost_bind_ids = fields.One2many(
        comodel_name='easypost.easypost.address',
        inverse_name='odoo_id',
        string='Easypost Bindings',
    )


@easypost
class EasypostAddressAdapter(EasypostCRUDAdapter):
    """ Backend Adapter for the Easypost EasypostAddress """
    _model_name = 'easypost.easypost.address'


@easypost
class EasypostAddressImportMapper(EasypostImportMapper):
    _model_name = 'easypost.easypost.address'

    direct = [
        (eval_false('street1'), 'street'),
        (eval_false('street2'), 'street2'),
        (eval_false('name'), 'name'),
        (eval_false('email'), 'email'),
        (eval_false('phone'), 'phone'),
        (eval_false('city'), 'city'),
        (eval_false('zip'), 'zip'),
        (eval_false('mode'), 'mode'),
    ]

    @mapping
    @only_create
    def partner_id(self, record):
        binder = self.binder_for(self._model_name)
        address_id = binder.to_odoo(record.id, browse=True)
        return {'partner_id': address_id.partner_id.id}

    @mapping
    def country_state_id(self, record):
        country_id = self.env['res.country'].search([
            ('code', '=', record.country),
        ],
            limit=1,
        )
        state_id = self.env['res.country.state'].search([
            ('country_id', '=', country_id.id),
            ('code', '=', record.state),
        ],
            limit=1,
        )
        return {'country_id': country_id.id,
                'state_id': state_id.id,
                }


@easypost
class EasypostAddressImporter(EasypostImporter):
    _model_name = ['easypost.easypost.address']
    _base_mapper = EasypostAddressImportMapper

    def _is_uptodate(self, binding):
        """Return False to always force import """
        return False


@easypost
class EasypostAddressExportMapper(EasypostExportMapper):
    _model_name = 'easypost.easypost.address'

    direct = [
        ('name', 'name'),
        ('street', 'street1'),
        ('street2', 'street2'),
        ('city', 'city'),
        ('zip', 'zip'),
        ('phone', 'phone'),
        ('email', 'email'),
        ('mode', 'mode'),
    ]

    @mapping
    def verify(self, record):
        return {'verify': ['delivery']}

    @mapping
    @changed_by('state_id')
    def state(self, record):
        return {'state': record.state_id.code}

    @mapping
    @changed_by('country_id')
    def country(self, record):
        if record.country_id:
            country = record.country_id.code
        else:
            country = record.company_id.country_id.code
        return {'country': country}


@easypost
class EasypostAddressExporter(EasypostExporter):
    _model_name = ['easypost.easypost.address']
    _base_mapper = EasypostAddressExportMapper

    def _after_export(self):
        """ Immediate re-import """
        importer = self.unit_for(EasypostAddressImporter)
        importer._update_export(self.binding_record, self.easypost_record)
