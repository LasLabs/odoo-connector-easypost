# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.connector.unit.mapper import (mapping,
                                                  # changed_by,
                                                  ImportMapper,
                                                  # ExportMapper,
                                                  )


def to_ord(field):
    """ A modifier intended to be used on the ``direct`` mappings.
    Convert a string to reversible ord representation (pads the zeros)
    Example::
        direct = [(to_ord('source'), 'target')]
    :param field: name of the source field in the record
    """
    def modifier(self, record, to_attr):
        value = record.get(field)
        if not value:
            return None
        ords = ['%03d' % ord(c) for c in value]
        return ''.join(ords)
    return modifier


def to_float(field):
    """ A modifier intended to be used on the ``direct`` mappings.
    Convert SQLAlchemy Decimal types to float
    Example::
        direct = [(to_float('source'), 'target')]
    :param field: name of the source field in the record
    """
    def modifier(self, record, to_attr):
        value = record.get(field)
        if not value:
            return False
        return float(value)
    return modifier


def to_int(field):
    """ A modifier intended to be used on the ``direct`` mappings.
    Convert SQLAlchemy Decimal types to integer
    Example::
        direct = [(to_int('source'), 'target')]
    :param field: name of the source field in the record
    """
    def modifier(self, record, to_attr):
        value = record.get(field)
        if not value:
            return False
        return int(value)
    return modifier


class EasypostImportMapper(ImportMapper):

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}
