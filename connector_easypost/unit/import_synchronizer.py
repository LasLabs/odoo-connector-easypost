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
from openerp import fields, _
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.connector import ConnectorUnit
from openerp.addons.connector.unit.synchronizer import Importer
from ..backend import easypost
from ..connector import get_environment, add_checkpoint


_logger = logging.getLogger(__name__)


class EasypostImporter(Importer):
    """ Base importer for Easypost """

    def __init__(self, connector_env):
        """
        :param connector_env: current environment (backend, session, ...)
        :type connector_env: :class:`connector.connector.ConnectorEnvironment`
        """
        super(EasypostImporter, self).__init__(connector_env)
        self.easypost_id = None
        self.easypost_record = None

    def _get_easypost_data(self):
        """ Return the raw Easypost data for ``self.easypost_id`` """
        _logger.debug('Getting EasyPost data for %s', self.easypost_id)
        return self.backend_adapter.read(self.easypost_id)

    def _before_import(self):
        """ Hook called before the import, when we have the Easypost
        data"""

    def _is_uptodate(self, binding):
        """Return True if the import should be skipped because
        it is already up-to-date in Odoo"""
        assert self.easypost_record
        if not self.easypost_record.updated_at:
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

    def _import_dependency(self, easypost_id, binding_model,
                           importer_class=None, always=False):
        """ Import a dependency.
        The importer class is a class or subclass of
        :class:`EasypostImporter`. A specific class can be defined.
        :param easypost_id: id of the related binding to import
        :param binding_model: name of the binding model for the relation
        :type binding_model: str | unicode
        :param importer_cls: :class:`odoo.addons.connector.\
                                     connector.ConnectorUnit`
                             class or parent class to use for the export.
                             By default: EasypostImporter
        :type importer_cls: :class:`odoo.addons.connector.\
                                    connector.MetaConnectorUnit`
        :param always: if True, the record is updated even if it already
                       exists, note that it is still skipped if it has
                       not been modified on Easypost since the last
                       update. When False, it will import it only when
                       it does not yet exist.
        :type always: boolean
        """
        if not easypost_id:
            return
        if importer_class is None:
            importer_class = EasypostImporter
        binder = self.binder_for(binding_model)
        if always or binder.to_odoo(easypost_id) is None:
            importer = self.unit_for(importer_class, model=binding_model)
            importer.run(easypost_id)

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
        return self.binder.to_odoo(self.easypost_id,
                                   unwrap=False,
                                   browse=True)

    def _create_data(self, map_record, **kwargs):
        return map_record.values(for_create=True, **kwargs)

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
            self.easypost_id)
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
            self.easypost_id)
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

    def run(self, easypost_id, force=False):
        """ Run the synchronization
        :param easypost_id: identifier of the record on Easypost
        """
        self.easypost_id = easypost_id
        if not self.easypost_record:
            self.easypost_record = self._get_easypost_data()
        _logger.info('self.easypost_record - %s', self.easypost_record)
        lock_name = 'import({}, {}, {}, {})'.format(
            self.backend_record._name,
            self.backend_record.id,
            self.model._name,
            easypost_id,
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
        self.binder.bind(self.easypost_id, binding)

        self._after_import(binding)


class BatchImporter(Importer):
    """ The role of a BatchImporter is to search for a list of
    items to import, then it can either import them directly or delay
    the import of each item separately.
    """

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


class DirectBatchImporter(BatchImporter):
    """ Import the records directly, without delaying the jobs. """
    _model_name = None

    def _import_record(self, record_id):
        """ Import the record directly """
        import_record(self.session,
                      self.model._name,
                      self.backend_record.id,
                      record_id)


class DelayedBatchImporter(BatchImporter):
    """ Delay import of the records """
    _model_name = None

    def _import_record(self, record_id, **kwargs):
        """ Delay the import of the records"""
        import_record.delay(self.session,
                            self.model._name,
                            self.backend_record.id,
                            record_id,
                            **kwargs)


@easypost
class SimpleRecordImporter(EasypostImporter):
    """ Import one Easypost Store """
    _model_name = []


@easypost
class AddCheckpoint(ConnectorUnit):
    """ Add a connector.checkpoint on the underlying model
    (not the easypost.* but the _inherits'ed model) """

    _model_name = ['easypost.easypost.address',
                   'easypost.product.category',
                   ]

    def run(self, odoo_binding_id):
        binding = self.model.browse(odoo_binding_id)
        record = binding.odoo_id
        add_checkpoint(self.session,
                       record._model._name,
                       record.id,
                       self.backend_record.id)


@job(default_channel='root.easypost')
def import_batch(session, model_name, backend_id, filters=None):
    """ Prepare a batch import of records from Easypost """
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(BatchImporter)
    importer.run(filters=filters)


@job(default_channel='root.easypost')
def import_record(session, model_name, backend_id, easypost_id, force=False):
    """ Import a record from Easypost """
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(EasypostImporter)
    _logger.debug('Importing CP Record %s from %s', easypost_id, model_name)
    importer.run(easypost_id, force=force)
