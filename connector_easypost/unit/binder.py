# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import openerp
from openerp.addons.connector.connector import Binder
from ..backend import easypost


class EasypostBinder(Binder):
    """ Generic Binder for Easypost """


@easypost
class EasypostModelBinder(EasypostBinder):
    """ Bindings are done directly on the binding model.
    Binding models are models called ``easypost.{normal_model}``,
    like ``easypost.res.partner`` or ``easypost.product.packaging``.
    They are ``_inherits`` of the normal models and contains
    the Easypost ID, the ID of the Easypost Backend and the additional
    fields belonging to the Easypost instance.
    """
    _model_name = [
        'easypost.easypost.address',
        'easypost.product.packaging',
        'easypost.stock.picking',
        'easypost.stock.picking.dispatch.rate',
        'easypost.shipping.label',
    ]

    def to_odoo(self, external_id, unwrap=True, browse=False):
        """ Give the Odoo ID for an external ID
        :param external_id: external ID for which we want the Odoo ID
        :param unwrap: if True, returns the normal record (the one
                       inherits'ed), else return the binding record
        :param browse: if True, returns a recordset
        :return: a recordset of one record, depending on the value of unwrap,
                 or an empty recordset if no binding is found
        :rtype: recordset
        """
        bindings = self.model.with_context(active_test=False).search([
            ('easypost_id', '=', str(external_id)),
            ('backend_id', '=', self.backend_record.id)
        ])
        if not bindings:
            return self.model.browse() if browse else None
        assert len(bindings) == 1, "Several records found: %s" % (bindings,)
        if unwrap:
            return bindings.odoo_id if browse else bindings.odoo_id.id
        else:
            return bindings if browse else bindings.id

    def to_backend(self, record_id, wrap=True):
        """ Give the external ID for an Odoo ID
        :param record_id: Odoo ID for which we want the external id
                          or a recordset with one record
        :param wrap: if False, record_id is the ID of the binding,
            if True, record_id is the ID of the normal record, the
            method will search the corresponding binding and returns
            the backend id of the binding
        :return: backend identifier of the record
        """
        record = self.model.browse()
        if isinstance(record_id, openerp.models.BaseModel):
            record_id.ensure_one()
            record = record_id
            record_id = record_id.id
        if wrap:
            binding = self.model.with_context(active_test=False).search([
                ('odoo_id', '=', record_id),
                ('backend_id', '=', self.backend_record.id),
            ])
            if binding:
                binding.ensure_one()
                return binding.easypost_id
            else:
                return None
        if not record:
            record = self.model.browse(record_id)
        assert record
        return record.easypost_id

    def bind(self, external_id, binding_id):
        """ Create the link between an external ID and an Odoo ID and
        update the last synchronization date.
        :param external_id: External ID to bind
        :param binding_id: Odoo ID to bind
        :type binding_id: int
        """
        if hasattr(external_id, 'id'):
            external_id = external_id.id
        # the external ID can be 0 on Easypost! Prevent False values
        # like False, None, or "", but not 0.
        assert (external_id or external_id == 0) and binding_id, (
            "external_id or binding_id missing, "
            "got: %s, %s" % (external_id, binding_id)
        )
        # avoid to trigger the export when we modify the `easypost_id`
        if not isinstance(binding_id, openerp.models.BaseModel):
            binding_id = self.model.browse(binding_id)
        binding_id.with_context(connector_no_export=True).write({
            'easypost_id': str(external_id),
            'sync_date': openerp.fields.Datetime.now(),
        })
        return binding_id

    def unwrap_binding(self, binding_id, browse=False):
        """ For a binding record, gives the normal record.
        Example: when called with a ``easypost.easypost.address`` id,
        it will return the corresponding ``product.product`` id.
        :param browse: when True, returns a browse_record instance
                       rather than an ID
        """
        if isinstance(binding_id, openerp.models.BaseModel):
            binding = binding_id
        else:
            binding = self.model.browse(binding_id)
        odoo_record = binding.odoo_id
        if browse:
            return odoo_record
        return odoo_record.id

    def unwrap_model(self):
        """ For a binding model, gives the name of the normal model.
        Example: when called on a binder for ``easypost.easypost.address``,
        it will return ``product.product``.
        This binder assumes that the normal model lays in ``odoo_id`` since
        this is the field we use in the ``_inherits`` bindings.
        """
        try:
            column = self.model._fields['odoo_id']
        except KeyError:
            raise ValueError('Cannot unwrap model %s, because it has '
                             'no odoo_id field' % self.model._name)
        return column.comodel_name
