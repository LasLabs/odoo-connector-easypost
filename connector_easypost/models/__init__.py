# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from . import easypost_backend
from . import easypost_binding

from . import address
from . import address_validate
from . import delivery_carrier
from . import parcel
from . import product_packaging
from . import rate
from . import res_company
from . import res_partner
from . import shipping_label
from . import shipment

# Must be imported after shipment
from . import sale
from . import sale_rate
