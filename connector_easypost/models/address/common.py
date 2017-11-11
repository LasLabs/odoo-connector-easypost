# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import models, fields, api

from odoo.addons.component.core import Component


_logger = logging.getLogger(__name__)


class EasypostAddress(models.TransientModel):
    """ Binding Model for the Easypost Address

        TransientModel so that records are eventually deleted due to immutable
        EasyPost objects
    """
    _name = 'easypost.address'
    _inherit = 'easypost.binding'
    _inherits = {'wizard.address.validate': 'odoo_id'}
    _description = 'Easypost Address'
    _easypost_model = 'Address'

    odoo_id = fields.Many2one(
        comodel_name='wizard.address.validate',
        string='Address Validator',
        required=True,
        ondelete='cascade',
    )
    phone = fields.Char(
        related='odoo_id.partner_id.phone',
        readonly=True,
    )
    email = fields.Char(
        related='odoo_id.partner_id.email',
        readonly=True,
    )
    name = fields.Char(
        related='odoo_id.partner_id.name',
        readonly=True,
    )
    company_name = fields.Char(
        related='odoo_id.partner_id.company_id.name',
        readonly=True,
    )

    @api.model
    def _get_by_partner(self, partner_id):
        return self.search([
            ('partner_id', '=', partner_id.id),
        ],
            limit=1,
        )


class WizardAddressValidate(models.TransientModel):
    """ Adds the ``one2many`` relation to the Easypost bindings
    (``easypost_bind_ids``)
    """
    _inherit = 'wizard.address.validate'

    easypost_bind_ids = fields.One2many(
        comodel_name='easypost.address',
        inverse_name='odoo_id',
        string='Easypost Bindings',
    )


class EasypostAddressAdapter(Component):
    """ Backend Adapter for the Easypost EasypostAddress """
    _name = 'easypost.address.adapter'
    _inherit = 'easypost.adapter'
    _apply_on = 'easypost.address'
