# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError

from .common import EasyPostSyncTestCase


model = 'odoo.addons.connector_easypost.models.easypost_backend'


class TestEasypostBackend(EasyPostSyncTestCase):

    def setUp(self):
        super(TestEasypostBackend, self).setUp()

    def test__check_default_for_company_raises_validation_error(self):
        """ Test _check_default_for_company raises `ValidationError`
        when creating a duplicate backend for a company """
        with self.assertRaises(ValidationError):
            self.env['easypost.backend'].create({
                'name': 'Test',
                'version': 'v2',
                'api_key': 'DUMMY',
            })
