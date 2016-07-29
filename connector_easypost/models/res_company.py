# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'
    easypost_backend_id = fields.Many2one(
        string='Default EasyPost Backend',
        comodel_name='easypost.backend',
        compute='_compute_easypost_backend_id',
    )

    @api.multi
    def _compute_easypost_backend_id(self):
        for rec_id in self:
            rec_id.easypost_backend_id = self.env['easypost.backend'].search([
                ('company_id', '=', rec_id.id),
                ('is_default', '=', True),
            ],
                limit=1
            ).id
