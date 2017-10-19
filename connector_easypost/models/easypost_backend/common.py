# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class EasypostBackend(models.Model):
    _name = 'easypost.backend'
    _description = 'Easypost Backend'
    _inherit = 'connector.backend',
    _inherits = {'address.validate': 'validator_id'}
    _backend_type = 'easypost'

    validator_id = fields.Many2one(
        string='Validator',
        comodel_name='address.validate',
        required=True,
        ondelete='cascade',
    )
    version = fields.Selection(
        selection='_get_versions',
        default='v2',
        required=True,
    )
    api_key = fields.Char(
        string='API Key',
        required=True,
        related='password',
    )
    is_default = fields.Boolean(
        default=True,
        help='Check this if this is the default connector for the company.'
        ' All newly created records for this company will be synced to the'
        ' default system. Only records that originated from non-default'
        ' systems will be synced with them.',
    )
    active = fields.Boolean(
        default=True,
    )
    company_id = fields.Many2one(
        string='Company',
        default=lambda s: s.env.user.company_id.id,
        comodel_name='res.company',
        compute='_compute_company_id',
        inverse='_inverse_company_id',
        search='_search_company_id',
    )
    is_default_address_validator = fields.Boolean(
        string='Default Address Validator',
        compute='_compute_is_default_address_validator',
        inverse='_inverse_is_default_address_validator',
    )

    @api.multi
    @api.constrains('is_default', 'company_id')
    def _check_default_for_company(self):
        for rec_id in self:
            domain = [
                ('company_id', '=', rec_id.company_id.id),
                ('is_default', '=', True),
            ]
            if len(self.search(domain)) > 1:
                raise ValidationError(_(
                    'This company already has a default EasyPost connector.',
                ))

    @api.multi
    def _compute_company_id(self):
        for record in self:
            record.company_id = record.company_ids.id

    @api.multi
    def _inverse_company_id(self):
        for record in self:
            record.company_ids = [(6, 0, record.company_id.ids)]

    @api.model
    def _search_company_id(self, op, val):
        if isinstance(val, int):
            val = [val]
        return [('company_ids', op, val)]

    @api.multi
    def _compute_is_default_address_validator(self):
        for record in self:
            default = record.company_id.default_address_validate_id
            is_default = (default == record.validator_id)
            record.is_default_address_validator = is_default

    @api.multi
    def _inverse_is_default_address_validator(self):
        for record in self:
            validator_id = record.validator_id.id
            record.company_id.default_address_validate_id = validator_id

    @api.model
    def _get_versions(self):
        """ Available versions in the backend.
        Can be inherited to add custom versions.  Using this method
        to add a version from an ``_inherit`` does not constrain
        to redefine the ``version`` field in the ``_inherit`` model.
        """
        return [('v2', 'v2')]

    @api.model
    def _get_interface_types(self):
        res = super(EasypostBackend, self)._get_interface_types()
        return res + [('easypost', 'EasyPost')]

    @api.model
    def create(self, vals):
        if not vals.get('validator_id'):
            validator = self.env['address.validate'].create({
                'name': vals['name'],
                'interface_type': 'easypost',
                'system_type': 'address.validate',
                'password': vals['api_key'],
            })
            vals['validator_id'] = validator.id
        return super(EasypostBackend, self).create(vals)

    @api.multi
    def unlink(self):
        if not self.env.context.get('no_validator_unlink'):
            for record in self:
                system = record.validator_id.with_context(
                    no_validator_unlink=True,
                )
                return system.unlink()
        else:
            return super(EasypostBackend, self).unlink()

    @api.multi
    def _import_all(self, model_name):
        for backend in self:
            self.env[model_name].with_delay().import_batch(backend)

    # Address Validation Interface
    def easypost_get_address(self, partner):
        return self.validator_id.easypost_get_address(None, partner)
