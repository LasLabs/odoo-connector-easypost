# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

"""
Helpers usable in the tests
"""

import importlib
import mock
from contextlib import contextmanager
import openerp.tests.common as common
from openerp.addons.connector.session import ConnectorSession
# from openerp.addons.connector_easypost.unit.import_synchronizer import (
#     import_batch,
# )
# from openerp.addons.connector_easypost.unit.backend_adapter import (
#     call_to_key,
# )
# from .data_base import easypost_base_responses


backend_adapter = 'openerp.addons.connector_easypost.unit.backend_adapter'


class TestResponder(object):
    """ Used to simulate the calls to Easypost.
    For a call (request) to Easypost, returns a stored
    response.
    """

    def __init__(self, responses, key_func=None):
        """
        The responses are stored in dict instances.
        The keys are normalized using the ``call_to_key``
        function which transform the request calls in a
        hashable form.
        :param responses: responses returned by Easypost
        :param call_to_key: function to build the key
            from the method and arguments
        :type responses: dict
        """
        self._responses = responses
        self._calls = []

    def __call__(self, method, arguments):
        self._calls.append((method, arguments))
        key = self.call_to_key(method, arguments)
        assert key in self._responses, (
            "%s not found in easypost responses" % str(key))
        if hasattr(self._responses[key], '__call__'):
            return self._responses[key]()
        else:
            return self._responses[key]


@contextmanager
def mock_job_delay_to_direct(job_path):
    """ Replace the .delay() of a job by a direct call
    job_path is the python path, such as::
      openerp.addons.easypost.stock_picking.export_picking_done
    """
    job_module, job_name = job_path.rsplit('.', 1)
    module = importlib.import_module(job_module)
    job_func = getattr(module, job_name, None)
    assert job_func, "The function %s must exist in %s" % (job_name,
                                                           job_module)

    def clean_args_for_func(*args, **kwargs):
        # remove the special args reseved to .delay()
        kwargs.pop('priority', None)
        kwargs.pop('eta', None)
        kwargs.pop('model_name', None)
        kwargs.pop('max_retries', None)
        kwargs.pop('description', None)
        job_func(*args, **kwargs)

    with mock.patch(job_path) as patched_job:
        # call the direct export instead of 'delay()'
        patched_job.delay.side_effect = clean_args_for_func
        yield patched_job


class ChainMap(dict):

    def __init__(self, *maps):
        self._maps = maps

    def __getitem__(self, key):
        for mapping in self._maps:
            try:
                return mapping[key]
            except KeyError:
                pass
        raise KeyError(key)

    def __contains__(self, key):
        try:
            self[key]
        except KeyError:
            return False
        else:
            return True


@contextmanager
def mock_api():
    """ """
    with mock.patch('%s.easypost' % backend_adapter) as API:
        api_mock = mock.MagicMock(name='easypost')
        API.return_value = api_mock
        api_mock.__enter__.return_value = api_mock
        yield API


class EasypostHelper(object):

    def __init__(self, cr, registry, model_name):
        self.cr = cr
        self.model = registry(model_name)

    def get_next_id(self):
        self.cr.execute("SELECT max(easypost_id::int) FROM %s " %
                        self.model._table)
        result = self.cr.fetchone()
        if result:
            return int(result[0] or 0) + 1
        else:
            return 1


class SetUpEasypostBase(common.TransactionCase):
    """ Base class - Test the imports from a Easypost Mock.
    The data returned by Easypost are those created for the
    demo version of Easypost on a standard 2 version.
    """

    def setUp(self):
        super(SetUpEasypostBase, self).setUp()
        self.backend_model = self.env['easypost.backend']
        self.session = ConnectorSession(
            self.env.cr, self.env.uid, context=self.env.context
        )
        self.backend = self.backend_model.create({
            'name': 'Test Easypost',
            'version': '2',
            'api_key': 'cueqNZUb3ldeWTNX7MU3Mel8UXtaAMUi',
        })
        self.backend_id = self.backend.id
        # payment method needed to import a purchase order
        workflow = self.env.ref(
            'sale_automatic_workflow.manual_validation'
        )
        journal = self.env.ref('account.check_journal')
        self.payment_term = self.env.ref(
            'account.account_payment_term_advance'
        )
        self.env['payment.method'].create({
            'name': 'checkmo',
            'workflow_process_id': workflow.id,
            'import_rule': 'always',
            'days_before_cancel': 0,
            'payment_term_id': self.payment_term.id,
            'journal_id': journal.id
        })

    def get_easypost_helper(self, model_name):
        return EasypostHelper(self.cr, self.registry, model_name)


class SetUpEasypostSynchronized(SetUpEasypostBase):

    def setUp(self):
        super(SetUpEasypostSynchronized, self).setUp()
