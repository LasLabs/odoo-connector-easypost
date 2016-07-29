# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
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
        """
        name = self.connector_env.model._easypost_model
        return getattr(self.easypost, name)

    def read(self, _id):
        """ Gets record by id and returns the object
        :param _id: Id of record to get from Db
        :type _id: int
        :return: EasyPost record for model
        """
        _logger.debug('Reading ID %s', _id)
        return self._get_ep_model().retrieve(_id)

    def create(self, data):
        """ Wrapper to create a record on the external system
        :param data: Data to create record with
        :type data: dict
        """
        _logger.debug('Creating w/ %s', data)
        return self._get_ep_model().create(**data)

    def update(self, _id, data):
        """ Wrapper to update a mutable record on external system
        :param _id: Id of record to get from Db
        :type _id: int
        :param data: Data to create record with
        :type data: dict
        """
        _logger.debug('Updating w/ %s', data)
        record = self.read(_id)
        if not hasattr(record, 'save'):
            record = self._get_ep_model().create(**data)
            return record
        for key, val in data.iteritems():
            setattr(record, key, val)
        record.save()
        return record
