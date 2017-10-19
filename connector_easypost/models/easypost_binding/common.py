# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models, fields, api
from odoo.addons.queue_job.job import job

_logger = logging.getLogger(__name__)


class EasypostBinding(models.AbstractModel):
    """Abstract model for all EasyPost binding models.

    All binding models should `_inherit` from this. They also need to declare
    the ``odoo_id`` Many2One field that relates to the Odoo record that the
    binding record represents.
    """
    _name = 'easypost.binding'
    _inherit = 'external.binding'
    _description = 'Easypost Binding Abstract'

    # odoo_id = odoo-side id must be declared in concrete model
    backend_id = fields.Many2one(
        comodel_name='easypost.backend',
        string='Easypost Backend',
        required=True,
        readonly=True,
        ondelete='restrict',
        default=lambda s: s._default_backend_id(),
    )
    external_id = fields.Char(
        string='ID on Easypost',
    )

    mode = fields.Char(
        help='EasyPost Mode',
    )
    created_at = fields.Date('Created At (on EasyPost)')
    updated_at = fields.Date('Updated At (on EasyPost)')

    _sql_constraints = [
        ('easypost_uniq', 'unique(backend_id, external_id)',
         'A binding already exists with the same Easypost ID.'),
    ]

    @api.model
    def _default_backend_id(self):
        return self.env['easypost.backend'].search([
            ('is_default', '=', True),
            ('active', '=', True),
        ],
            limit=1,
        )

    @api.model
    @job(default_channel='root.easypost')
    def import_batch(self, backend, filters=None):
        """Prepare the import of records modified in EasyPost."""
        if filters is None:
            filters = {}
        with backend.work_on(self._name) as work:
            importer = work.component(usage='batch.importer')
            return importer.run(filters=filters)

    @api.model
    def import_direct(self, backend, external_record):
        """Directly import a data record."""
        with backend.work_on(self._name) as work:
            importer = work.component(usage='record.importer')
            return importer.run(
                external_record.id,
                external_record=external_record,
                force=True,
            )

    @api.model
    @job(default_channel='root.easypost')
    def import_record(self, backend, external_id, force=False):
        """Import an EasyPost record."""
        with backend.work_on(self._name) as work:
            importer = work.component(usage='record.importer')
            return importer.run(external_id, force=force)

    @api.model_cr_context
    def ensure_bindings(self, odoo_records, force=False, export=False,
                        external_id=None, company=None):
        bindings = odoo_records.easypost_bind_ids.with_context(
            connector_no_export=True,
        )
        for record in odoo_records:
            if record.easypost_bind_ids and not force:
                continue
            try:
                company = (company or
                           record.company_id or
                           self.env.user.company_id
                           )
            except AttributeError:
                company = self.env.user.company_id
            if company.easypost_backend_id:
                vals = {
                    'odoo_id': record.id,
                    'backend_id': company.easypost_backend_id.id,
                }
                if external_id:
                    vals['external_id'] = external_id
                new_binding = bindings.create(vals)
                bindings += new_binding
            if export:
                exporter = new_binding.with_context(
                    connector_no_export=False,
                )
                exporter.export_record()

    @api.multi
    @job(default_channel='root.easypost')
    def export_record(self, fields=None):
        self.ensure_one()
        with self.backend_id.work_on(self._name) as work:
            exporter = work.component(usage='record.exporter')
            _logger.debug(
                'Exporting "%s" with fields "%s"', self, fields or 'all',
            )
            return exporter.run(self, fields)

    @api.model
    @job(default_channel='root.easypost')
    def export_delete_record(self, backend, external_id):
        """Delete a record on EasyPost."""
        with backend.work_on(self._name) as work:
            deleter = work.component(usage='record.exporter.deleter')
            return deleter.run(external_id)
