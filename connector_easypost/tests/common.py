# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# Copyright 2013-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

# pylint: disable=missing-manifest-dependency
# disable warning on 'vcr' missing in manifest: this is only a dependency for
# dev/tests

"""
Helpers usable in the tests
"""

import xmlrpclib
import logging

import mock
import odoo

from contextlib import contextmanager
from os.path import dirname, join
from odoo import models
from odoo.addons.component.tests.common import SavepointComponentCase

from vcr import VCR

logging.getLogger("vcr").setLevel(logging.WARNING)

recorder = VCR(
    record_mode='once',
    cassette_library_dir=join(dirname(__file__), 'fixtures/cassettes'),
    path_transformer=VCR.ensure_suffix('.yaml'),
    filter_headers=['Authorization'],
    decode_compressed_response=True,
)


class MockResponseImage(object):

    def __init__(self, resp_data, code=200, msg='OK'):
        self.resp_data = resp_data
        self.code = code
        self.msg = msg
        self.headers = {'content-type': 'image/jpeg'}

    def read(self):
        # pylint: disable=W8106
        return self.resp_data

    def getcode(self):
        return self.code


@contextmanager
def mock_urlopen_image():
    with mock.patch('urllib2.urlopen') as urlopen:
        urlopen.return_value = MockResponseImage('')
        yield


class EasyPostHelper(object):

    def __init__(self, cr, registry, model_name):
        self.cr = cr
        self.model = registry(model_name)

    def get_next_id(self):
        self.cr.execute("SELECT max(external_id::int) FROM %s " %
                        self.model._table)
        result = self.cr.fetchone()
        if result:
            return int(result[0] or 0) + 1
        else:
            return 1


class EasyPostTestCase(SavepointComponentCase):
    """ Base class - Test the imports from a EasyPost Mock.

    The data returned by EasyPost are those created for the
    demo version of EasyPost on a standard 1.9 version.
    """

    def setUp(self):
        super(EasyPostTestCase, self).setUp()
        # disable commits when run from pytest/nosetest
        odoo.tools.config['test_enable'] = True

        self.backend_model = self.env['easypost.backend']
        self.warehouse = self.env.ref('stock.warehouse0')
        self.backend = self.backend_model.create(
            {'name': 'Test EasyPost',
             'version': 'v2',
             'api_key': '',
             'company_id': self.env.user.company_id.id,
             'is_default': True,
             'is_default_address_validator': True,
             }
        )

    def get_easypost_helper(self, model_name):
        return EasyPostHelper(self.cr, self.registry, model_name)

    def create_binding_no_export(self, model_name, odoo_id, external_id=None,
                                 **cols):
        if isinstance(odoo_id, models.BaseModel):
            odoo_id = odoo_id.id
        values = {
            'backend_id': self.backend.id,
            'odoo_id': odoo_id,
            'external_id': external_id,
        }
        if cols:
            values.update(cols)
        return self.env[model_name].with_context(
            connector_no_export=True,
        ).create(values)

    @contextmanager
    def mock_with_delay(self):
        with mock.patch(
                'odoo.addons.queue_job.models.base.DelayableRecordset',
                name='DelayableRecordset', spec=True
        ) as delayable_cls:
            # prepare the mocks
            delayable = mock.MagicMock(name='DelayableBinding')
            delayable_cls.return_value = delayable
            yield delayable_cls, delayable

    def parse_cassette_request(self, body):
        args, __ = xmlrpclib.loads(body)
        # the first argument is a hash, we don't mind
        return args[1:]

    def _get_external(self, external_id):
        with self.backend.work_on(self.model._name) as work:
            adapter = work.component(usage='backend.adapter')
            return adapter.read(external_id)

    def _import_record(self, model_name, easypost_id, cassette=True):
        assert model_name.startswith('easypost.')
        table_name = model_name.replace('.', '_')
        # strip 'easypost_' from the model_name to shorted the filename
        filename = 'import_%s_%s' % (table_name[8:], str(easypost_id))

        def run_import():
            with mock_urlopen_image():
                self.env[model_name].import_record(self.backend, easypost_id)

        if cassette:
            with recorder.use_cassette(filename):
                run_import()
        else:
            run_import()

        binding = self.env[model_name].search(
            [('backend_id', '=', self.backend.id),
             ('external_id', '=', str(easypost_id))]
        )
        self.assertEqual(len(binding), 1)
        return binding

    def assert_records(self, expected_records, records):
        """ Assert that a recordset matches with expected values.

        The expected records are a list of nametuple, the fields of the
        namedtuple must have the same name than the recordset's fields.

        The expected values are compared to the recordset and records that
        differ from the expected ones are show as ``-`` (missing) or ``+``
        (extra) lines.

        Example::

            ExpectedShop = namedtuple('ExpectedShop',
                                      'name company_id')
            expected = [
                ExpectedShop(
                    name='MyShop1',
                    company_id=self.company_ch
                ),
                ExpectedShop(
                    name='MyShop2',
                    company_id=self.company_ch
                ),
            ]
            self.assert_records(expected, shops)

        Possible output:

         - foo.shop(name: MyShop1, company_id: res.company(2,))
         - foo.shop(name: MyShop2, company_id: res.company(1,))
         + foo.shop(name: MyShop3, company_id: res.company(1,))

        :param expected_records: list of namedtuple with matching values
                                 for the records
        :param records: the recordset to check
        :raises: AssertionError if the values do not match
        """
        model_name = records._name
        records = list(records)
        assert len(expected_records) > 0, "must have > 0 expected record"
        fields = expected_records[0]._fields
        not_found = []
        equals = []
        for expected in expected_records:
            for record in records:
                for field, value in expected._asdict().iteritems():
                    if not getattr(record, field) == value:
                        break
                else:
                    records.remove(record)
                    equals.append(record)
                    break
            else:
                not_found.append(expected)
        message = []
        for record in equals:
            # same records
            message.append(
                u' ✓ {}({})'.format(
                    model_name,
                    u', '.join(u'%s: %s' % (field, getattr(record, field)) for
                               field in fields)
                )
            )
        for expected in not_found:
            # missing records
            message.append(
                u' - {}({})'.format(
                    model_name,
                    u', '.join(u'%s: %s' % (k, v) for
                               k, v in expected._asdict().iteritems())
                )
            )
        for record in records:
            # extra records
            message.append(
                u' + {}({})'.format(
                    model_name,
                    u', '.join(u'%s: %s' % (field, getattr(record, field)) for
                               field in fields)
                )
            )
        if not_found or records:
            raise AssertionError(u'Records do not match:\n\n{}'.format(
                '\n'.join(message)
            ))


class EasyPostSyncTestCase(EasyPostTestCase):

    def setUp(self):
        super(EasyPostSyncTestCase, self).setUp()
        self.easypost_carrier = self.env.ref(
            'connector_easypost.delivery_carrier_usps_priority',
        )
        self.product = self.env.ref('product.product_product_7')

    def _create_parcel(self, export=True, dispatch_package=None, vals=None):
        """Create a parcel and optionally export."""

        if dispatch_package is None:
            dispatch_package = self.env.ref(
                'connector_easypost.SmallFlatRateBox',
            )

        model = self.env['easypost.parcel'].with_context(
            connector_no_export=True,
        )
        self.record_vals = {
            'name': 'Test Parcel',
            'packaging_id': dispatch_package.id,
            'shipping_weight': 50,
        }
        if vals is not None:
            self.record_vals.update(vals)

        self.record = model.create(self.record_vals)
        if export:
            self.record.export_record()
        return self.record

    def _create_partner(self, validated=False, name=None, street=None,
                        zip_code=None):
        if name is None:
            name = 'The White House'
        if street is None:
            street = '1600 Pennsylvania'
        if zip_code is None:
            zip_code = '20500'
        partner = self.env['res.partner'].create({
            'name': name,
            'street': street,
            'zip': zip_code,
        })
        if validated:
            partner.write(
                self.backend.easypost_get_address(partner),
            )
        return partner

    def _create_quant(self, qty=1, weight=3):
        """Create a new ``stock.quant`` of ``qty`` and ``weight``."""
        self.qty = qty
        self.weight = weight
        return self.env['stock.quant'].create({
            'location_id': self.warehouse.lot_stock_id.id,
            'product_id': self.product.id,
            'qty': qty,
            'weight': weight,
        })

    def _create_shipment(self, export=True, to_partner=None):
        """Create a shipment and optionally export."""

        if to_partner is None:
            to_partner = self._create_partner(validated=True)

        model = self.env['easypost.shipment'].with_context(
            connector_no_export=True,
        )
        warehouse = self.warehouse
        warehouse.partner_id = self._create_partner(
            True, 'Twitter', '1355 Market Street #900', '94103',
        )
        location_dest = self.env.ref('stock.stock_location_3')
        quant = self._create_quant()
        parcel = self._create_parcel()
        self.record_vals = {
            'location_dest_id': location_dest.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'move_type': 'direct',
            'picking_type_id': warehouse.out_type_id.id,
            'weight_uom_id': self.env.ref('product.product_uom_inch').id,
            'partner_id': to_partner.id,
            'pack_operation_ids': [(0, 0, {
                'location_dest_id': location_dest.id,
                'location_id': warehouse.out_type_id.id,
                'product_id': quant.product_id.id,
                'product_uom': quant.product_id.uom_id.id,
                'ordered_qty': quant.qty,
                'qty_done': quant.qty,
                'weight_uom_id': parcel.weight_uom_id.id,
                'result_package_id': parcel.odoo_id.id,
            })]
        }

        self.record = model.create(self.record_vals)
        if export:
            self.record.export_record()
        return self.record

    def _create_sale(self, to_partner=None):
        """Create a sale and optionally export."""

        if to_partner is None:
            to_partner = self._create_partner(validated=True)

        self.record = self.env['easypost.sale'].create({
            'partner_id': to_partner.id,
            'carrier_id': self.easypost_carrier.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 79.00,
                'name': self.product.display_name,
                'customer_lead': 0.00,
            })]
        })
        return self.record
