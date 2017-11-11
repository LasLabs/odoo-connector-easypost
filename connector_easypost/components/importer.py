# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


"""
Importers for Easypost.
An import can be skipped if the last sync date is more recent than
the last update in Easypost.
They should call the ``bind`` method if the binder even if the records
are already bound, to update the last sync date.
"""


import logging
import dateutil.parser
import pytz
from hashlib import md5
from odoo import fields, _
from odoo.addons.component.core import AbstractComponent
from odoo.addons.queue_job.exception import NothingToDoJob


_logger = logging.getLogger(__name__)


class EasypostImporter(AbstractComponent):
    """ Base importer for Easypost """

    _name = 'easypost.importer'
    _inherit = ['base.importer', 'base.easypost.connector']
    _usage = 'record.importer'

    def __init__(self, work_context):
        super(EasypostImporter, self).__init__(work_context)
        self.external_id = None
        self.easypost_record = None

    def _get_easypost_data(self):
        """ Return the raw Easypost data for ``self.external_id`` """
        _logger.debug('Getting EasyPost data for %s', self.external_id)
        return self.backend_adapter.read(self.external_id)

    def _before_import(self):
        """ Hook called before the import, when we have the Easypost
        data"""

    def _is_uptodate(self, binding):
        """Return True if the import should be skipped because
        it is already up-to-date in Odoo"""
        assert self.easypost_record
        if not getattr(self.easypost_record, 'updated_at', False):
            return  # no update date on Easypost, always import it.
        if not binding:
            return  # it does not exist so it should not be skipped
        sync = binding.sync_date
        if not sync:
            return
        sync_date = fields.Datetime.from_string(sync)
        sync_date = pytz.utc.localize(sync_date)
        easypost_date = self.easypost_record.updated_at
        easypost_date = dateutil.parser.parse(easypost_date)
        # if the last synchronization date is greater than the last
        # update in easypost, we skip the import.
        # Important: at the beginning of the exporters flows, we have to
        # check if the easypost_date is more recent than the sync_date
        # and if so, schedule a new import. If we don't do that, we'll
        # miss changes done in Easypost
        return easypost_date < sync_date

    def _import_dependency(self, external_id, binding_model,
                           importer=None, always=False):
        """Import a dependency.
        Args:
            external_id (int): ID of the external record to import.
            binding_model (basestring): Name of the model to bind to.
            importer (AbstractComponent, optional): Importer to use.
            always (bool, optional): Always update the record, regardless
                of if it exists in Odoo already. Note that if the record
                hasn't changed, it still may be skipped.
        """
        if not external_id:
            return
        binder = self.binder_for(binding_model)
        if always or not binder.to_internal(external_id):
            if importer is None:
                importer = self.component(usage='record.importer',
                                          model_name=binding_model)
            try:
                importer.run(external_id)
            except NothingToDoJob:
                _logger.info(
                    'Dependency import of %s(%s) has been ignored.',
                    binding_model._name, external_id
                )

    def _import_dependencies(self):
        """ Import the dependencies for the record
        Import of dependencies can be done manually or by calling
        :meth:`_import_dependency` for each dependency.
        """
        return

    def _map_data(self):
        """ Returns an instance of
        :py:class:`~odoo.addons.connector.unit.mapper.MapRecord`
        """
        return self.mapper.map_record(self.easypost_record)

    def _validate_data(self, data):
        """ Check if the values to import are correct
        Pro-actively check before the ``_create`` or
        ``_update`` if some fields are missing or invalid.
        Raise `InvalidDataError`
        """
        return

    def _must_skip(self):
        """ Hook called right after we read the data from the backend.
        If the method returns a message giving a reason for the
        skipping, the import will be interrupted and the message
        recorded in the job (if the import is called directly by the
        job, not by dependencies).
        If it returns None, the import will continue normally.
        :returns: None | str | unicode
        """
        return

    def _get_binding(self):
        return self.binder.to_internal(self.external_id)

    def _generate_external_id(self):
        """ Some objects in EasyPost have no ID. Return one based on
        the unique data of the object
        :return str: The MD5 Hex Digest of the record
        """
        obj_hash = md5()
        for attr in self._hashable_attrs:
            obj_hash.update(getattr(self.easypost_record, attr, '') or '')
        return '%s_%s' % (self._id_prefix, obj_hash.hexdigest())

    def _create(self, data):
        """ Create the Odoo record """
        # special check on data before import
        self._validate_data(data)
        model = self.model.with_context(connector_no_export=True)
        _logger.debug('Creating with %s', data)
        binding = model.create(data)
        _logger.debug(
            '%d created from easypost %s',
            binding,
            self.external_id)
        return binding

    def _update_data(self, map_record, **kwargs):
        return map_record.values(**kwargs)

    def _update(self, binding, data):
        """ Update an Odoo record """
        # special check on data before import
        self._validate_data(data)
        binding.with_context(connector_no_export=True).write(data)
        _logger.debug(
            '%d updated from easypost %s',
            binding,
            self.external_id)
        return

    def _update_export(self, bind_record, easypost_record):
        """ Update record using data received from export """
        self.easypost_record = easypost_record
        map_record = self._map_data()
        record = self._update_data(map_record)
        self._update(bind_record, record)

    def _after_import(self, binding):
        """ Hook called at the end of the import """
        return

    def _create_data(self, map_record, **kwargs):
        return map_record.values(for_create=True, **kwargs)

    def run(self, external_id=None, force=False, external_record=None):
        """ Run the synchronization.

        Args:
            external_id (int | easypost.BaseModel): identifier of the
                record in HelpScout, or a HelpScout record.
            force (bool, optional): Set to ``True`` to force the sync.
            external_record (easypost.models.BaseModel): Record from
                HelpScout. Defining this will force the import of this
                record, instead of the search of the remote.

        Returns:
            str: Canonical status message.
        """

        if external_record:
            self.easypost_record = external_record

        assert external_id or self.easypost_record

        self.external_id = external_id

        if not self.easypost_record:
            self.easypost_record = self._get_easypost_data()
        else:
            if not external_id:
                self.external_id = self._generate_external_id()
            if not getattr(self.easypost_record, 'id', None):
                self.easypost_record.id = self.external_id

        _logger.debug('self.easypost_record - %s', self.easypost_record)
        lock_name = 'import({}, {}, {}, {})'.format(
            self.backend_record._name,
            self.backend_record.id,
            self.model._name,
            external_id,
        )
        # Keep a lock on this import until the transaction is committed
        self.advisory_lock_or_retry(lock_name)

        skip = self._must_skip()
        if skip:
            return skip

        binding = self._get_binding()

        if not force and self._is_uptodate(binding):
            return _('Already up-to-date.')
        self._before_import()

        # import the missing linked resources
        self._import_dependencies()

        map_record = self._map_data()
        _logger.debug('Mapped to %s', map_record)

        if binding:
            record = self._update_data(map_record)
            self._update(binding, record)
        else:
            record = self._create_data(map_record)
            binding = self._create(record)
        self.binder.bind(self.external_id, binding)

        self._after_import(binding)
        return binding


class BatchImporter(AbstractComponent):
    """ The role of a BatchImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

    _name = 'easypost.batch.importer'
    _inherit = ['base.importer', 'base.easypost.connector']
    _usage = 'batch.importer'

    def run(self, filters=None):
        """ Run the synchronization """
        record_ids = self.backend_adapter.search(filters)
        for record_id in record_ids:
            self._import_record(record_id)

    def _import_record(self, record_id):
        """ Import a record directly or delay the import of the record.
        Method to implement in sub-classes.
        """
        raise NotImplementedError


class DirectBatchImporter(AbstractComponent):
    """ Import the records directly, without delaying the jobs. """
    _model_name = None

    _name = 'easypost.direct.batch.importer'
    _inherit = 'easypost.batch.importer'

    def _import_record(self, external_id, **kwargs):
        """Import the record directly."""
        self.model.import_record(self.backend_record, external_id, **kwargs)


class DelayedBatchImporter(AbstractComponent):
    """ Delay import of the records """
    _model_name = None

    _name = 'easypost.delayed.batch.importer'
    _inherit = 'easypost.batch.importer'

    def _import_record(self, external_id, job_options=None, **kwargs):
        """Delay the record imports."""
        delayed = self.model.with_delay(**job_options or {})
        delayed.import_record(self.backend_record, external_id, **kwargs)
