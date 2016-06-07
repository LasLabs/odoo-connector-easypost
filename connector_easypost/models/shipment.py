# -*- coding: utf-8 -*-
# © 2015 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp import models, fields
from openerp.addons.connector.unit.mapper import (mapping,
                                                  changed_by,
                                                  # only_create,
                                                  )
from ..unit.backend_adapter import EasypostCRUDAdapter
from ..unit.mapper import (EasypostImportMapper,
                           EasypostExportMapper,
                           )
from ..backend import easypost
from ..unit.import_synchronizer import (EasypostImporter)
from ..unit.export_synchronizer import (EasypostExporter)
from ..unit.mapper import eval_false
from .stock_delivery_rate import StockDeliveryRateImporter


_logger = logging.getLogger(__name__)


class EasypostEasypostShipment(models.Model):
    """ Binding Model for the Easypost EasypostShipment """
    _name = 'easypost.easypost.shipment'
    _inherit = 'easypost.binding'
    _inherits = {'easypost.shipment': 'odoo_id'}
    _description = 'Easypost EasypostShipment'
    _easypost_model = 'Shipment'

    odoo_id = fields.Many2one(
        comodel_name='easypost.shipment',
        string='EasypostShipment',
        required=True,
        ondelete='cascade',
    )

    _sql_constraints = [
        ('odoo_uniq', 'unique(backend_id, odoo_id)',
         'A Easypost binding for this record already exists.'),
    ]


class EasypostShipment(models.Model):
    """ Adds the ``one2many`` relation to the Easypost bindings
    (``easypost_bind_ids``)
    """
    _name = 'easypost.shipment'
    _description = 'Easypost Shipment'

    to_partner_id = fields.Many2one(
        string='To Address',
        comodel_name='res.partner',
        related='group_id.ship_partner_id',
    )
    from_partner_id = fields.Many2one(
        string='From Address',
        comodel_name='res.partner',
        related='group_id.from_partner_id',
    )
    group_id = fields.Many2one(
        string='Delivery Group',
        comodel_name='stock.delivery.group',
        required=True,
    )
    pack_id = fields.Many2one(
        string='Delivery Package',
        comodel_name='stock.delivery.pack',
        related='group_id.pack_id',
    )

    easypost_bind_ids = fields.One2many(
        comodel_name='easypost.easypost.shipment',
        inverse_name='odoo_id',
        string='Easypost Bindings',
    )


@easypost
class EasypostShipmentAdapter(EasypostCRUDAdapter):
    """ Backend Adapter for the Easypost EasypostShipment """
    _model_name = 'easypost.easypost.shipment'


@easypost
class EasypostShipmentImportMapper(EasypostImportMapper):
    _model_name = 'easypost.easypost.shipment'

    direct = [
        (eval_false('mode'), 'mode'),
    ]

    @mapping
    def rates(self, record):
        importer = self.unit_for(StockDeliveryRateImporter,
                                 model='easypost.stock.delivery.rate')
        for rate in record.rates:
            importer.run(rate.id)


@easypost
class EasypostShipmentImporter(EasypostImporter):
    _model_name = ['easypost.easypost.shipment']
    _base_mapper = EasypostShipmentImportMapper

    def _is_uptodate(self, binding):
        """Return False to always force import """
        return False


@easypost
class EasypostShipmentExportMapper(EasypostExportMapper):
    _model_name = 'easypost.easypost.shipment'

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
    @changed_by('pack_id')
    def parcel(self, record):
        binder = self.binder_for('easypost.stock.delivery.pack')
        parcel = binder.to_backend(record.pack_id)
        return {'parcel': {'id': parcel}}

    @mapping
    @changed_by('to_partner_id')
    def to_address(self, record):
        return {'to_address': self._map_partner(record.to_partner_id)}

    @mapping
    @changed_by('from_partner_id')
    def from_address(self, record):
        return {'from_address': self._map_partner(record.from_partner_id)}


@easypost
class EasypostShipmentExporter(EasypostExporter):
    _model_name = ['easypost.easypost.shipment']
    _base_mapper = EasypostShipmentExportMapper

    def _export_dependencies(self):
        _logger.debug('Exporting Dependency %r', self.binding_record.pack_id)
        self._export_dependency(self.binding_record.pack_id,
                                'easypost.stock.delivery.pack')

    def _after_export(self):
        """ Immediate re-import """
        importer = self.unit_for(StockDeliveryRateImporter,
                                 model='easypost.stock.delivery.rate')
        for rate in self.easypost_record.rates:
            importer.easypost_record = rate
            importer.run(rate.id)
