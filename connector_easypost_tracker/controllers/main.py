# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from json import loads, dumps
from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.addons.connector_easypost.unit.import_synchronizer import (
    create_connector_session,
    import_data,
)


class EasypostWebhookController(http.Controller):

    EVENTS = {'tracker.updated': 'easypost.stock.picking.tracking.group'}

    def _get_backend(self, env):
        return env['easypost.backend'].sudo().search([
            ('is_default', '=', True),
        ])

    @http.route([
        '/connector_easypost_tracker/webhook',
    ], type='http', auth='none', csrf=False)
    def easypost_webhook(self):
        """ Handle requests from the EasyPost Webhook """
        req = loads(request.httprequest.data)
        model = self.EVENTS.get(req.get('description'))
        if model:
            # We need to escalate to SUPERUSER in order to
            # access protected models. Open to suggestions here
            request.env.uid = SUPERUSER_ID
            backend = self._get_backend(request.env)
            session = create_connector_session(request.env, model, backend.id)
            import_data.delay(session, model, backend.id,
                              dumps(req.get('result')))
        return 'ok'
