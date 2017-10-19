# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.addons.component.core import AbstractComponent


_logger = logging.getLogger(__name__)

try:
    import easypost
except ImportError:
    _logger.warning('Could not import module dependency `easypost`')


class EasypostAdapter(AbstractComponent):
    """ External Records Adapter for Easypost """

    _name = 'easypost.adapter'
    _inherit = ['base.backend.adapter', 'base.easypost.connector']
    _usage = 'backend.adapter'

    def __init__(self, connector_env):
        """ Ready the DB adapter
        :param connector_env: current environment (backend, session, ...)
        :type connector_env: :class:`connector.connector.ConnectorEnvironment`
        """
        super(EasypostAdapter, self).__init__(connector_env)
        backend = self.backend_record
        self.easypost = easypost
        self.easypost.api_key = backend.api_key

    def _get_ep_model(self):
        """ Get the correct model object by name from Easypost lib
        """
        name = self.env[self.work.model_name]._easypost_model
        return getattr(self.easypost, name)

    # pylint: disable=W8106
    def read(self, _id):
        """ Gets record by id and returns the object
        :param _id: Id of record to get from Db
        :type _id: int
        :return: EasyPost record for model
        """
        _logger.debug('Reading ID %s', _id)
        return self._get_ep_model().retrieve(_id)

    # pylint: disable=W8106
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
