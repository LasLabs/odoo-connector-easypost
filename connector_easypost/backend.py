# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.addons.connector.backend as backend


easypost = backend.Backend('easypost')
easypost2 = backend.Backend(parent=easypost, version='2')
