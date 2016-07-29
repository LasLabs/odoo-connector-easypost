# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
# from openerp.addons.connector_easypost.unit.import_synchronizer import (
#     import_batch,
#     import_record,
# )
# from .common import (mock_api,
#                       SetUpEasypostBase,
#                       SetUpEasypostSynchronized,
#                       )
#
#
# class TestBaseEasypost(SetUpEasypostBase):
#     def test_import_backend(self):
#         """ Synchronize initial metadata """
#         with mock_api():
#             import_batch(
#                 self.session, 'easypost.medical.pharmacy', self.backend_id
#             )
#
#         store_model = self.env['easypost.medical.pharmacy']
#         stores = store_model.search([('backend_id', '=', self.backend_id)])
#         self.assertEqual(len(stores), 2)
#
#
# class TestImportEasypost(SetUpEasypostSynchronized):
#     """ Test the imports from a Easypost Mock. """
#
#     def test_import_product_category(self):
#         """ Import of a product category """
#         backend_id = self.backend_id
#         with mock_api():
#             import_record(self.session, 'easypost.product.category',
#                           backend_id, 1)
#
#         category_model = self.env['easypost.product.category']
#         category = category_model.search([('backend_id', '=', backend_id)])
#         self.assertEqual(len(category), 1)
