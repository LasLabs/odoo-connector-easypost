# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api
from odoo import models


class AddressValidate(models.Model):
    _inherit = 'address.validate'

    @api.model
    def _get_interface_types(self):
        res = super(AddressValidate, self)._get_interface_types()
        return res + [('easypost', 'EasyPost')]

    @api.multi
    def easypost_get_client(self):
        """Handled in the adapters."""

    @api.multi
    def easypost_test_connection(self):
        """Handled in the adapters."""

    @api.multi
    def easypost_get_address(self, api_client, partner):
        wizard = self.env['easypost.address'].create({
            'partner_id': partner.id,
            'interface_id': self.id,
        })
        wizard.export_record()
        return {
            'street': wizard.street,
            'street2': wizard.street2,
            'city': wizard.city,
            'zip': wizard.zip,
            'state_id': wizard.state_id.id,
            'country_id': wizard.country_id.id,
            'validation_messages': wizard.validation_messages,
            'latitude': wizard.latitude,
            'longitude': wizard.longitude,
            'is_valid': wizard.is_valid,
        }
