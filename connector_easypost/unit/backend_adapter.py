# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import easypost
from openerp.addons.connector.unit.backend_adapter import CRUDAdapter


_logger = logging.getLogger(__name__)


class EasypostCRUDAdapter(CRUDAdapter):
    """ External Records Adapter for Easypost """

    def __init__(self, connector_env):
        """ Ready the DB adapter
        :param connector_env: current environment (backend, session, ...)
        :type connector_env: :class:`connector.connector.ConnectorEnvironment`
        """
        super(EasypostCRUDAdapter, self).__init__(connector_env)
        backend = self.backend_record
        self.easypost = easypost
        self.easypost.api_key = backend.api_key

    def _get_ep_model(self):
        """ Get the correct model object by name from Easypost lib
        :rtype: :class:`sqlalchemy.schema.Table`
        """
        name = self.connector_env.model._easypost_model
        return getattr(self.easypost, name)

    def read(self, _id):
        """ Gets record by id and returns the object
        :param _id: Id of record to get from Db
        :type _id: int
        :return: EasyPost record for model
        """
        return self._get_ep_model().retrieve(_id)

    def create(self, data):
        """ Wrapper to create a record on the external system
        :param data: Data to create record with
        :type data: dict
        :rtype: :class:`sqlalchemy.ext.declarative.Declarative`
        """
        return self._get_ep_model().create(**data)
