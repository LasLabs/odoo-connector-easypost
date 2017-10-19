# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import requests
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create

from ...components.mapper import inner_attr


class ShippingLabelImportMapper(Component):
    _name = 'easypost.import.mapper.shipping.label'
    _inherit = 'easypost.import.mapper'
    _apply_on = 'easypost.shipping.label'

    direct = [
        (inner_attr('postage_label', 'id'), 'external_id'),
    ]

    @mapping
    def package_id(self, record):
        binder = self.binder_for('easypost.parcel')
        package_id = binder.to_odoo(record.parcel.id)
        return {'package_id': package_id}

    @mapping
    @only_create
    def datas(self, record):
        label = requests.get(record.postage_label.label_url)
        return {'datas': label.content.encode('base64')}

    @mapping
    @only_create
    def picking_id(self, record):
        binder = self.binder_for('easypost.rate')
        rate = self.env['stock.picking.rate'].browse(
            binder.to_odoo(record.selected_rate.id)
        )
        return {'picking_id': rate.picking_id.id}

    @mapping
    @only_create
    def rate_id(self, record):
        binder = self.binder_for('easypost.rate')
        rate_id = binder.to_odoo(record.selected_rate.id)
        return {'rate_id': rate_id}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @mapping
    def name(self, record):
        return {'name': record.postage_label.label_url.split('/')[-1]}

    @mapping
    def tracking_url(self, record):
        tracking_url = ''
        if record.tracker:
            tracking_url = record.tracker.public_url
        return {'tracking_url': tracking_url}

    @mapping
    def tracking_number(self, record):
        tracking_number = ''
        if record.tracker:
            tracking_number = record.tracker.tracking_code
        return {'tracking_number': tracking_number}

    @mapping
    def file_type(self, record):
        return {'file_type': 'pdf'}


class ShippingLabelImporter(Component):
    _name = 'easypost.record.importer.shipping.label'
    _inherit = 'easypost.importer'
    _apply_on = 'easypost.shipping.label'
