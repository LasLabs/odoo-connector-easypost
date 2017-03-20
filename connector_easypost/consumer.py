# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.connector.event import on_record_create, on_record_write

from .connector import get_environment
from .models.stock_picking import EasypostStockPickingAdapter
from .unit.export_synchronizer import export_record


import logging
_logger = logging.getLogger(__name__)

QUANT_DEPENDS = 'product_pack_tmpl_id'


@on_record_create(model_names=['easypost.easypost.address'])
@on_record_write(model_names=['easypost.easypost.address'])
def immediate_export(session, model_name, record_id, vals):
    """ Create immediate export of a binding record.
    (A binding record being a ``easypost.easypost.address``,
    ``easypost.easypost.address``, ...)
    """
    if session.context.get('connector_no_export'):
        return
    fields = vals.keys()
    export_record(session, model_name, record_id, fields=fields)


@on_record_write(model_names=['easypost.address'])
def immediate_export_all_bindings(session, model_name, record_id, vals):
    """ Create immediate export of all the bindings of a record.
    In this case, it is called on records of normal models and will delay
    the export for all the bindings.
    """
    if session.context.get('connector_no_export'):
        return
    record = session.env[model_name].browse(record_id)
    fields = vals.keys()
    for binding in record.easypost_bind_ids:
        export_record(session, binding._name, binding.id,
                      fields=fields)


@on_record_create(model_names=['easypost.stock.quant.package'])
def delay_export(session, model_name, record_id, vals):
    """ Delay a job which exports a binding record.
    (A binding record being a ``easypost.stock.quant.package``,
    ``easypost.easypost.address``, ...)
    """
    if session.context.get('connector_no_export'):
        return
    fields = vals.keys()
    export_record.delay(session, model_name, record_id, fields=fields)


@on_record_write(model_names=['stock.quant.package'])
def export_package_change(session, model_name, record_id, vals):
    """ Delay a job which export all the bindings of a `stock.quant.package`.
    In this case, it is called on records of normal models and will delay
    the export for all the bindings. If dependencies are met, export shipment.
    """
    if session.context.get('connector_no_export'):
        return
    if not vals.get(QUANT_DEPENDS):
        _logger.debug('Not exporting %s because of missing dependencies',
                      model_name)
        return
    record = session.env[model_name].browse(record_id)
    fields = vals.keys()
    for binding in record.easypost_bind_ids:
        export_record.delay(session, binding._name, binding.id,
                            fields=fields)
    if record.picking_ids:
        picking = record.picking_ids[0]
        pick_vals = picking._fields.keys()
        for binding in picking.easypost_bind_ids:
            export_record.delay(session, binding._name, binding.id,
                                fields=pick_vals)


@on_record_create(model_names=['stock.picking'])
def create_picking_no_export(session, model_name, record_id, vals):
    """ Create a new binding record then do nothing """
    model_obj = session.env['easypost.%s' % model_name].with_context(
        connector_no_export=True,
    )
    if not len(model_obj.search([('odoo_id', '=', record_id)])):
        model_obj.create({
            'odoo_id': record_id,
        })


@on_record_create(model_names=['stock.quant.package'])
def create_quant_package_no_export(session, model_name, record_id, vals):
    """ Create a new binding record and export """
    model_obj = session.env['easypost.%s' % model_name].with_context(
        connector_no_export=True,
    )
    if not len(model_obj.search([('odoo_id', '=', record_id)])):
        model_obj.create({
            'odoo_id': record_id,
        })
    return export_package_change(session, model_name, record_id, vals)


@on_record_write(model_names=['stock.picking.rate'])
def immediate_buy_shipment(session, model_name, record_id, vals):
    """ Trigger immediate purchase workflow for a Shipment """
    record = session.env[model_name].browse(record_id)
    if record.is_purchased:
        env = get_environment(
            session,
            'easypost.stock.picking',
            record.easypost_bind_ids.backend_id.id,
        )
        unit = env.get_connector_unit(EasypostStockPickingAdapter)
        return unit.buy(record.easypost_bind_ids)


@on_record_write(model_names=['stock.picking.rate'])
def immediate_cancel_shipment(session, model_name, record_id, vals):
    """ Trigger immediate cancelation workflow for a Shipment """
    record = session.env[model_name].browse(record_id)
    if record.state == 'cancel':
        env = get_environment(
            session,
            'easypost.stock.picking',
            record.easypost_bind_ids.backend_id.id,
        )
        unit = env.get_connector_unit(EasypostStockPickingAdapter)
        return unit.cancel(record.easypost_bind_ids)
