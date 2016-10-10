# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.addons.connector.connector import ConnectorEnvironment
from openerp.addons.connector.checkpoint import checkpoint


def get_environment(session, model_name, backend_id):
    """ Create an environment to work with.  """
    backend_record = session.env['easypost.backend'].browse(backend_id)
    env = ConnectorEnvironment(backend_record, session, model_name)
    lang = backend_record.default_lang_id
    lang_code = lang.code if lang else 'en_US'
    if lang_code == session.context.get('lang'):
        return env
    else:
        with env.session.change_context(lang=lang_code):
            return env


class EasypostBinding(models.AbstractModel):
    """ Abstract Model for the Bindigs.
    All the models used as bindings between Easypost and Odoo
    (``easypost.easypost.address``, ``easypost.easypost.address``, ...) should
    ``_inherit`` it.
    """
    _name = 'easypost.binding'
    _inherit = 'external.binding'
    _description = 'Easypost Binding (abstract)'

    # odoo_id = odoo-side id must be declared in concrete model
    backend_id = fields.Many2one(
        comodel_name='easypost.backend',
        string='Easypost Backend',
        required=True,
        readonly=True,
        ondelete='restrict',
        default=lambda s: s._default_backend_id(),
    )
    easypost_id = fields.Char(string='ID on Easypost')

    mode = fields.Char(
        help='EasyPost Mode',
    )
    created_at = fields.Date('Created At (on EasyPost)')
    updated_at = fields.Date('Updated At (on EasyPost)')

    _sql_constraints = [
        ('easypost_uniq', 'unique(backend_id, easypost_id)',
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


def add_checkpoint(session, model_name, record_id, backend_id):
    """ Add a row in the model ``connector.checkpoint`` for a record,
    meaning it has to be reviewed by a user.
    :param session: current session
    :type session: :class:`odoo.addons.connector.session.ConnectorSession`
    :param model_name: name of the model of the record to be reviewed
    :type model_name: str
    :param record_id: ID of the record to be reviewed
    :type record_id: int
    :param backend_id: ID of the Easypost Backend
    :type backend_id: int
    """
    return checkpoint.add_checkpoint(session, model_name, record_id,
                                     'easypost.backend', backend_id)
