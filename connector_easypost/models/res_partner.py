# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_carrier = fields.Boolean()

    @api.multi
    def action_easypost_synchronize(self):
        self.ensure_one()
        try:
            address_id = self._easypost_synchronize()[self.id]
        except KeyError:
            raise ValidationError(_(
                'An error occurred - most likely no EasyPost configured.',
            ))
        context = self.env.context.copy()
        model_obj = self.env['ir.model.data']
        form_id = model_obj.xmlid_to_object(
            'connector_easypost.easypost_address_view_form',
        )
        action_id = model_obj.xmlid_to_object(
            'connector_easypost.action_easypost_address',
        )
        context.update({
            'active_id': self.id,
        })
        return {
            'name': action_id.name,
            'help': action_id.help,
            'type': action_id.type,
            'view_mode': 'form',
            'view_id': form_id.id,
            'views': [
                (form_id.id, 'form'),
            ],
            'target': 'new',
            'context': context,
            'res_model': action_id.res_model,
            'res_id': address_id.odoo_id.id,
        }

    @api.multi
    def _easypost_synchronize(self, auto=False):
        """ Get address data from EasyPost, sync w/ partner if auto

        @TODO: Maybe this should be in the wizard model. Seems weird to
            split the logic of the action and the sync though

        Params:
            auto: Automatically bind address data to partner

        Returns:
            :type:``dict`` Dict of addresses that were created,
                keyed by partner id
        """
        res = {}
        address_obj = self.env['easypost.easypost.address']
        for rec_id in self:
            if rec_id.company_id.easypost_backend_id:
                backend_id = rec_id.company_id.easypost_backend_id
                address_id = address_obj._get_by_partner(rec_id)
                if not address_id:
                    address_id = address_obj.create({
                        'partner_id': rec_id.id,
                        'backend_id': backend_id.id,
                    })
                elif not auto:
                    # @TODO: remove duplicate eval of auto
                    address_id.odoo_id._sync_from_partner()
                if auto:
                    partner_vals = {}
                    for key in address_id.odoo_id.SYNC_ATTRS:
                        val = getattr(address_id, key, '')
                        val = val.id if hasattr(val, 'id') else val
                        partner_vals[key] = val
                    _logger.debug('Writing new address to %s %s',
                                  rec_id, partner_vals)
                    rec_id.write(partner_vals)
                res[rec_id.id] = address_id
        return res
