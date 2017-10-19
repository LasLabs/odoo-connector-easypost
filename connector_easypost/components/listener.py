# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent, Component
from odoo.addons.component_event import skip_if


QUANT_DEPENDS = 'packaging_id'


class EasyPostListener(AbstractComponent):
    """Generic event listener for EasyPost."""
    _name = 'easypost.listener'
    _inherit = 'base.event.listener'

    def new_binding(self, record, force=False):
        record.easypost_bind_ids.ensure_bindings(record, force)

    def no_connector_export(self, record):
        return self.env.context.get('connector_no_export', False)

    def export_record(self, record, fields=None):
        record.with_delay().export_record(fields=fields)

    def delete_record(self, record):
        record.with_delay().export_delete_record()


class EasyPostListenerOdooDelayed(AbstractComponent):
    """Generic event listener for Odoo models delayed export changes."""
    _name = 'easypost.listener.odoo.delayed'
    _inherit = 'easypost.listener'

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_create(self, record, fields=None):
        self.new_binding(record)
        self.export_record(record.easypost_bind_ids, fields)

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_write(self, record, fields=None):
        if not record.easypost_bind_ids:
            return
        self.export_record(record.easypost_bind_ids, fields)


class EasyPostListenerStockQuantPackage(Component):
    """Event listener for stock.quant.package"""
    _name = 'easypost.listener.stock.quant.package'
    _inherit = 'easypost.listener.odoo.delayed'
    _apply_on = 'stock.quant.package'

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_create(self, record, fields=None):
        self.new_binding(record)
        self.on_record_write(record, fields=fields)

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_write(self, record, fields=None):

        if not record[QUANT_DEPENDS]:
            # Not exporting because no package
            return

        super(EasyPostListenerStockQuantPackage, self).on_record_write(record)

        for bind in record.picking_ids.mapped('easypost_bind_ids'):
            self.export_record(bind)


# class EasyPostListenerSaleOrder(Component):
#     """Event listener for sale.order"""
#     _name = 'easypost.listener.sale.order'
#     _inherit = 'easypost.listener'
#     _apply_on = 'sale.order'
#
#     def is_easypost(self, record):
#         return record.carrier_id.delivery_type == 'easypost'
#
#     def is_non_easypost(self, record):
#         return self.no_connector_export(record) or \
#                not self.is_easypost(record)
#
#     @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
#     def on_record_create(self, record, fields=None):
#         self.new_binding(record)
#         if record.carrier_id.delivery_type == 'easypost':
#             self.on_record_write(record, fields=fields)
#
#     @skip_if(lambda self, record, **kwargs: self.is_non_easypost(record))
#     def on_record_write(self, record, fields=None):
#         record.easypost_bind_ids.export_record(fields=fields)


# class EasyPostListenerStockPicking(Component):
#     """Event listener for stock.picking"""
#     _name = 'easypost.listener.stock.picking'
#     _inherit = 'easypost.listener'
#     _apply_on = 'stock.picking'
#
#     @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
#     def on_record_create(self, record, fields=None):
#         self.new_binding(record)
#         self.on_record_write(record, fields=fields)
#
#     @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
#     def on_record_write(self, record, fields=None):
#         self.export_record(record.easypost_bind_ids)
