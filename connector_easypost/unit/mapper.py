# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.connector.unit.mapper import (mapping,
                                                  # changed_by,
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


class EasypostImportMapper(ImportMapper):

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}

    @mapping
    def easypost_id(self, record):
        return {'easypost_id': record.id}


class EasypostExportMapper(ExportMapper):

    @mapping
    def id(self, record):
        return {'id': record.easypost_id}
