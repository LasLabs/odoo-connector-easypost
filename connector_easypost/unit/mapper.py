# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.connector.unit.mapper import (mapping,
                                                  only_create,
                                                  ImportMapper,
                                                  ExportMapper,
                                                  )


def eval_false(field):
    """ A modifier intended to be used on the ``direct`` mappings.
    Convert "false" String to None
    Example::
        direct = [(eval_false('source'), 'target')]
    :param field: name of the source field in the record
    """
    def modifier(self, record, to_attr):
        value = getattr(record, field, None)
        if str(value).lower() == 'false':
            return None
        return value
    return modifier


def inner_attr(attr, field):
    """ A modifier intended to be used on the ``direct`` mappings.
    Looks inside of an object for the field, using attr arg
    Example::
        direct = [(inside_key('source', 'attr'), 'target')]
    :param attr: name of object attribute to look inside of
    :param field: name of the source field in the record
    """
    def modifier(self, record, to_attr):
        value = None
        record_attr = getattr(record, attr, None)
        if record_attr is not None:
            value = getattr(record_attr, field, None)
        return value
    return modifier


class EasypostImportMapper(ImportMapper):

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @mapping
    def easypost_id(self, record):
        return {'easypost_id': record.id}

    @mapping
    @only_create
    def odoo_id(self, record):
        """ Attempt to bind on an existing record
        EasyPost aggregates records upstream, this is to handle that
        """
        binder = self.binder_for(self._model_name)
        odoo_id = binder.to_odoo(record.id)
        if odoo_id:
            return {'odoo_id': odoo_id}


class EasypostExportMapper(ExportMapper):

    @mapping
    def id(self, record):
        return {'id': record.easypost_id}
