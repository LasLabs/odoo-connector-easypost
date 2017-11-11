# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    easypost_backend_id = fields.Many2one(
        string='Default EasyPost Backend',
        comodel_name='easypost.backend',
        compute='_compute_easypost_backend_id',
    )

    @api.multi
    def _compute_easypost_backend_id(self):
        for record in self:
            backend = self.env['easypost.backend'].search([
                ('company_id', '=', record.id),
                ('is_default', '=', True),
            ],
                limit=1
            )
            record.easypost_backend_id = backend
