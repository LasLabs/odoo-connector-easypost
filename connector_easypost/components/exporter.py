# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import dateutil.parser
import threading
import pytz

from contextlib import contextmanager
import psycopg2

import odoo
from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import (
    IDMissingInBackend,
    RetryableJobError,
)
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


"""
Exporters for Easypost.
In addition to its export job, an exporter has to:
* check in Easypost if the record has been updated more recently than the
  last sync date and if yes, delay an import
* call the ``bind`` method of the binder to update the last sync date
"""


class EasypostBaseExporter(AbstractComponent):
    """ Base exporter for Easypost """

    _name = 'easypost.exporter.base'
    _inherit = ['base.exporter', 'base.easypost.connector']
    _usage = 'record.exporter'

    def __init__(self, working_context):
        super(EasypostBaseExporter, self).__init__(working_context)
        self.binding_id = None
        self.external_id = None

    def _delay_import(self):
        """ Schedule an import of the record.
        Adapt in the sub-classes when the model is not imported
        using ``import_record``.
        """
        # force is True because the sync_date will be more recent
        # so the import would be skipped
        assert self.external_id
        self.binding.with_delay().import_record(
            self.backend_record, self.external_id, force=True,
        )

    def _should_import(self):
        """ Before the export, compare the update date
        in Easypost and the last sync date in Odoo,
        if the former is more recent, schedule an import
        to not miss changes done in Easypost.
        """
        assert self.binding_record
        if not self.external_id:
            return False
        sync = self.binding_record.sync_date
        if not sync:
            return True
        record = self.backend_adapter.read(self.external_id)
        if not record.updated_at:
            # If empty, the record is immutable. Return not changed
            return True
        sync_date = odoo.fields.Datetime.from_string(sync)
        sync_date = pytz.utc.localize(sync_date)
        easypost_date = dateutil.parser.parse(record.updated_at)
        return sync_date < easypost_date

    def _get_odoo_data(self):
        """ Return the raw Odoo data for ``self.binding_id`` """
        return self.model.browse(self.binding_id)

    def run(self, binding, *args, **kwargs):
        """Run the synchronization.
        Args:
            binding (EasyPostBinding): Binding record to export.
        """
        self.binding_id = binding.id
        self.binding_record = self._get_odoo_data()
        self.binding = self.binding_record

        self.external_id = self.binder.to_backend(self.binding_record)

        try:
            should_import = self._should_import()
        except IDMissingInBackend:
            self.external_id = None
            should_import = False

        if should_import:
            self._delay_import()

        result = self._run(*args, **kwargs)

        self.binder.bind(self.external_id, self.binding_record)

        # Commit so we keep the external ID when there are several
        # exports (due to dependencies) and one of them fails.
        # The commit will also release the lock acquired on the binding
        # record
        if not getattr(threading.currentThread(), 'testing', None):
            self.env.cr.commit()  # pylint: disable=E8102

        self._after_export()

        return result

    def _run(self):
        """ Flow of the synchronization, implemented in inherited classes"""
        raise NotImplementedError

    def _after_export(self):
        """ Can do several actions after exporting a record on easypost """


class EasypostExporter(EasypostBaseExporter):
    """ A common flow for the exports to Easypost """

    _name = 'easypost.exporter'
    _inherit = 'easypost.exporter.base'

    def __init__(self, connector_env):
        """
        :param connector_env: current environment (backend, session, ...)
        :type connector_env: :class:`connector.connector.ConnectorEnvironment`
        """
        super(EasypostExporter, self).__init__(connector_env)
        self.binding_record = None

    def _lock(self):
        """Lock the binding record.

        Lock the binding record so we are sure that only one export
        job is running for this record if concurrent jobs have to export the
        same record.

        When concurrent jobs try to export the same record, the first one
        will lock and proceed, the others will fail to lock and will be
        retried later.

        This behavior works also when the export becomes multilevel
        with :meth:`_export_dependencies`. Each level will set its own lock
        on the binding record it has to export.
        """
        # pylint: disable=E8103
        sql = 'SELECT id FROM %s WHERE ID = %%s FOR UPDATE NOWAIT' % (
            self.model._table,
        )
        try:
            self.env.cr.execute(sql, (self.binding_id, ),
                                log_exceptions=False)
        except psycopg2.OperationalError:
            _logger.info(
                'A concurrent job is already exporting the same record (%s '
                'with id %s). Job delayed.',
                self.model._name, self.binding_id,
            )
            raise RetryableJobError(_(
                'A concurrent job is already exporting the same record '
                '(%s with id %s). The job will be retried later.'
            ) % (
                self.model._name, self.binding_id,
            ))

    def _has_to_skip(self):
        """ Return True if the export can be skipped """
        return False

    @contextmanager
    def _retry_unique_violation(self):
        """ Context manager: catch Unique constraint error and retry the
        job later.
        When we execute several jobs workers concurrently, it happens
        that 2 jobs are creating the same record at the same time (binding
        record created by :meth:`_export_dependency`), resulting in:
            IntegrityError: duplicate key value violates unique
            constraint "easypost_product_product_odoo_uniq"
            DETAIL:  Key (backend_id, odoo_id)=(1, 4851) already exists.
        In that case, we'll retry the import just later.
        .. warning:: The unique constraint must be created on the
                     binding record to prevent 2 bindings to be created
                     for the same Easypost record.
        """
        try:
            yield
        except psycopg2.IntegrityError as err:
            if err.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
                raise RetryableJobError(
                    'A database error caused the failure of the job:\n'
                    '%s\n\n'
                    'Likely due to 2 concurrent jobs wanting to create '
                    'the same record. The job will be retried later.' % err)
            else:
                raise

    def _export_dependency(self, relation, binding_model,
                           component_usage='record.exporter',
                           binding_field='easypost_bind_ids',
                           binding_extra_vals=None):
        """Export a dependency.

        The exporter class is a subclass of ``HelpScoutExporter``. The
        ``exporter_class`` parameter can be used to modify this behavior.

        Warning:
            A commit is performed at the end of the export of each dependency.
            This is in order to maintain the integrity of any records that
            the external system contains.
            You must take care to not modify the Odoo database while an export
            is happening, except when writing back the external ID or to
            eventually store external data on this side.
            This method should only be called at the beginning of the exporter
            syncrhonization (in :meth:`~._export_dependencies`.)

        Args:
            relation (odoo.models.BaseModel): Record to export.
            binding_model (basestring): Name of the binding model for the
                relation
            component_usage (basestring): ``usage`` to look for when finding
                the ``Component`` for the export. Default ``record.exporter``.
            binding_field (basestring): Name of the one2many field on a normal
                record that points to the binding record. It is only used when
                 ``relation`` is a normal record instead of a binding.
            binding_exra_vals (dict):
        """
        if not relation:
            return
        rel_binder = self.binder_for(binding_model)
        # wrap is typically True if the relation is for instance a
        # 'product.product' record but the binding model is
        # 'easypost.product.product'
        wrap = relation._name != binding_model

        if wrap and hasattr(relation, binding_field):
            domain = [('odoo_id', '=', relation.id),
                      ('backend_id', '=', self.backend_record.id)]
            binding = self.env[binding_model].search(domain)
            if binding:
                assert len(binding) == 1, (
                    'only 1 binding for a backend is '
                    'supported in _export_dependency')
            # we are working with a unwrapped record (e.g.
            # product.category) and the binding does not exist yet.
            # Example: I created a product.product and its binding
            # easypost.product.product and we are exporting it, but we need to
            # create the binding for the product.category on which it
            # depends.
            else:
                bind_values = {'backend_id': self.backend_record.id,
                               'odoo_id': relation.id}
                if binding_extra_vals:
                    bind_values.update(binding_extra_vals)
                # If 2 jobs create it at the same time, retry
                # one later. A unique constraint (backend_id,
                # odoo_id) should exist on the binding model
                with self._retry_unique_violation():
                    binding = (self.env[binding_model]
                               .with_context(connector_no_export=True)
                               .sudo()
                               .create(bind_values))
                    # Eager commit to avoid having 2 jobs
                    # exporting at the same time. The constraint
                    # will pop if an other job already created
                    # the same binding. It will be caught and
                    # raise a RetryableJobError.
                    if not getattr(
                            threading.currentThread(), 'testing', None,
                    ):
                        self.env.cr.commit()  # pylint: disable=E8102
        else:
            # If easypost_bind_ids does not exist we are typically in a
            # "direct" binding (the binding record is the same record).
            # If wrap is True, relation is already a binding record.
            binding = relation

        if not rel_binder.to_external(binding):
            exporter = self.component(usage=component_usage,
                                      model_name=binding_model)
            exporter.run(binding)

    def _export_dependencies(self):
        """ Export the dependencies for the record"""
        return

    def _map_data(self):
        """ Returns an instance of
        :py:class:`~odoo.addons.connector.unit.mapper.MapRecord`
        """
        return self.mapper.map_record(self.binding_record)

    def _validate_data(self, data):
        """ Check if the values to import are correct
        Kept for retro-compatibility. To remove in 8.0
        Pro-actively check before the ``Model.create`` or ``Model.update``
        if some fields are missing or invalid
        Raise `InvalidDataError`
        """
        _logger.warning('Deprecated: _validate_data is deprecated '
                        'in favor of validate_create_data() '
                        'and validate_update_data()')
        self._validate_create_data(data)
        self._validate_update_data(data)

    def _validate_create_data(self, data):
        """ Check if the values to import are correct
        Pro-actively check before the ``Model.create`` if some fields
        are missing or invalid
        Raise `InvalidDataError`
        """
        return

    def _validate_update_data(self, data):
        """ Check if the values to import are correct
        Pro-actively check before the ``Model.update`` if some fields
        are missing or invalid
        Raise `InvalidDataError`
        """
        return

    def _create_data(self, map_record, fields=None, **kwargs):
        """ Get the data to pass to :py:meth:`_create` """
        return map_record.values(for_create=True, fields=fields, **kwargs)

    def _create(self, data):
        """ Create the Easypost record """
        # special check on data before export
        self._validate_create_data(data)
        self.easypost_record = self.backend_adapter.create(data)
        return self.easypost_record

    def _update_data(self, map_record, fields=None, **kwargs):
        """ Get the data to pass to :py:meth:`_update` """
        return map_record.values(fields=fields, **kwargs)

    def _update(self, data):
        """ Update an Easypost record """
        assert self.external_id
        # special check on data before export
        self._validate_update_data(data)
        self.easypost_record = self.backend_adapter.update(
            self.external_id, data,
        )
        return self.easypost_record

    def _run(self, fields=None):
        """ Flow of the synchronization, implemented in inherited classes """
        assert self.binding_id
        assert self.binding_record

        if not self.external_id:
            fields = None  # should be created with all the fields

        if self._has_to_skip():
            return

        # export the missing linked resources
        self._export_dependencies()

        # prevent other jobs to export the same record
        # will be released on commit (or rollback)
        self._lock()

        map_record = self._map_data()

        if self.external_id:
            record = self._update_data(map_record, fields=fields)
            if not record:
                return _('Nothing to export.')
            self._update(record)
        else:
            record = self._create_data(map_record, fields=fields)
            if not record:
                return _('Nothing to export.')
            self.external_id = self._create(record)
        return _(
            'Record exported on Easypost w/ ID %r' % self.external_id
        )
