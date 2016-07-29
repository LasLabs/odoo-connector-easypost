# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from datetime import datetime
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.addons.connector.session import ConnectorSession
from ..unit.import_synchronizer import (import_batch,
                                        DirectBatchImporter,
                                        )
from ..backend import easypost

_logger = logging.getLogger(__name__)


class EasypostBackend(models.Model):
    _name = 'easypost.backend'
    _description = 'Easypost Backend'
    _inherit = 'connector.backend'

    _backend_type = 'easypost'

    name = fields.Char(required=True)
    version = fields.Selection(
        selection='select_versions',
        required=True,
    )
    api_key = fields.Char(
        string='API Key',
        required=True,
    )
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        default=lambda s: s.env.ref('base.main_company'),
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
    default_lang_id = fields.Many2one(
        comodel_name='res.lang',
        string='Default Language',
        help="If a default language is selected, the records "
             "will be imported in the translation of this language.\n"
             "Note that this is not actually implemented.",
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

    @api.model
    def __get_session(self):
        return ConnectorSession(
            self.env.cr, self.env.uid, context=self.env.context,
        )

    @api.model
    def select_versions(self):
        """ Available versions in the backend.
        Can be inherited to add custom versions.  Using this method
        to add a version from an ``_inherit`` does not constrain
        to redefine the ``version`` field in the ``_inherit`` model.
        """
        return [('2', 'v2')]

    @api.multi
    def check_easypost_structure(self):
        """ Used in each data import.
        Verify if a store exists for each backend before starting the import.
        """
        for backend in self:
            backend.synchronize_metadata()
        return True

    @api.multi
    def synchronize_metadata(self):
        # session = self.__get_session()
        for backend in self:
            pass
        return True

    @api.multi
    def _import_all(self, model):
        session = self.__get_session()
        for backend in self:
            backend.check_easypost_structure()
            import_batch.delay(session, model, backend.id)

    @api.multi
    def output_recorder(self):
        """ Utility method to output a file containing all the recorded
        requests / responses with Easypost.  Used to generate test data.
        Should be called with ``erppeek`` for instance.
        """
        from .unit.backend_adapter import output_recorder
        import os
        import tempfile
        fmt = '%Y-%m-%d-%H-%M-%S'
        timestamp = datetime.now().strftime(fmt)
        filename = 'output_%s_%s' % (self.env.cr.dbname, timestamp)
        path = os.path.join(tempfile.gettempdir(), filename)
        output_recorder(path)
        return path


@easypost
class MetadataBatchImporter(DirectBatchImporter):
    """ Import the records directly, without delaying the jobs.
    Import the Easypost Stores
    They are imported directly because this is a rare and fast operation,
    and we don't really bother if it blocks the UI during this time.
    (that's also a mean to rapidly check the connectivity with Easypost).
    """
    _model_name = []
