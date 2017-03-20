# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from .common import SetUpEasypostBase


model = 'odoo.addons.connector_easypost.models.easypost_backend'


class TestEasypostBackend(SetUpEasypostBase):

    def setUp(self):
        super(TestEasypostBackend, self).setUp()

    def test__check_default_for_company_raises_validation_error(self):
        """ Test _check_default_for_company raises `ValidationError`
        when creating a duplicate backend for a company """
        with self.assertRaises(ValidationError):
            self.env['easypost.backend'].create({
                'name': 'Test',
                'version': '2',
                'api_key': 'DUMMY',
            })

    def test_check_easypost_structure(self):
        """ Test check_easypost_structure returns True """
        rec = self.get_easypost_backend()
        self.assertTrue(
            rec.check_easypost_structure()
        )

    def test_synchronize_metadata(self):
        """ Test check_easypost_structure returns True """
        rec = self.get_easypost_backend()
        self.assertTrue(
            rec.synchronize_metadata()
        )
