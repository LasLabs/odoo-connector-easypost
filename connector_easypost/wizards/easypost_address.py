# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields


import logging
_logger = logging.getLogger(__name__)


class EasypostAddress(models.TransientModel):
    _name = "easypost.address"

    SYNC_ATTRS = [
        'street', 'street2', 'city', 'state_id', 'company_id',
        'country_id', 'phone', 'email', 'name', 'zip',
    ]

    partner_id = fields.Many2one(
        string='Partner',
        comodel_name='res.partner',
        required=True,
        default=lambda s: s._default_partner_id(),
        readonly=True,
    )
    name = fields.Char(
        readonly=True,
    )
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        readonly=True,
    )
    street = fields.Char(
        readonly=True,
    )
    street2 = fields.Char(
        readonly=True,
    )
    city = fields.Char(
        readonly=True,
    )
    zip = fields.Char(
        readonly=True,
    )
    state_id = fields.Many2one(
        string='State',
        comodel_name='res.country.state',
        readonly=True,
    )
    country_id = fields.Many2one(
        string='Country',
        comodel_name='res.country',
        readonly=True,
    )
    phone = fields.Char(
        readonly=True,
    )
    email = fields.Char(
        readonly=True,
    )
    mode = fields.Char(
        help='EasyPost response mode.',
        readonly=True,
    )

    @api.multi
    def _default_partner_id(self):
        partner_id = self.env['res.partner'].browse(
            self.env.context.get('active_id')
        )
        if partner_id:
            return partner_id.id

    @api.model
    def create(self, vals):
        partner_id = self.env['res.partner'].browse(vals['partner_id'])
        for key in self.SYNC_ATTRS:
            if not vals.get(key):
                val = getattr(partner_id, key, '')
                vals[key] = val.id if hasattr(val, 'id') else val
        return super(EasypostAddress, self).create(vals)

    @api.multi
    def _sync_from_partner(self):
        for rec_id in self:
            vals = {}
            for key in self.SYNC_ATTRS:
                val = getattr(rec_id.partner_id, key, '')
                vals[key] = val.id if hasattr(val, 'id') else val
            rec_id.write(vals)

    # @api.multi
    # @api.onchange(*SYNC_ATTRS)
    # def _onchange_sync_attrs(self):
    #     for rec_id in self:
    #         for attr in rec_id.SYNC_ATTRS:
    #             setattr(rec_id, attr, getattr(rec_id, attr))

    @api.multi
    def action_validate(self):
        for rec_id in self:
            rec_id.partner_id._easypost_synchronize(auto=True)

    # @api.model
    # def _get_by_partner(self, partner_id):
    #     return self.search([
    #         ('partner_id', '=', partner_id.id),
    #     ],
    #         limit=1,
    #     )
