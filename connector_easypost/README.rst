.. image:: https://img.shields.io/badge/license-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================
EasyPost Connector
==================

This module provides EasyPost connector functionality.


Installation
============

To install this module, you need to:

* Install Python dependencies -
  ``pip install easypost``
* Install OCA Connector module from https://github.com/OCA/connector
* Since we are not using OCA/stock-logistics-workflow/9.0, you must clone
``stock-logistics-workflow`` from https://github.com/laslabs/stock-logistics-workflow.git
  and checkout the ``feature/9.0/LABS-187-migrate-connectoreasypost-to-oca`` branch.
  You will be able to use OCA stock-logistics-workflow once the following MRs are merged to 9.0:
  https://github.com/OCA/stock-logistics-workflow/pull/247
  https://github.com/OCA/stock-logistics-workflow/pull/238
* Clone OCA/carrier-delivery/9.0 from ``https://github.com/OCA/carrier-delivery.git``
  and install ``base_delivery_carrier_label``
* Install Easypost Connector module
* Restart Odoo (requirement of any new connector to set proper DB triggers)

Configuration
=============

To configure this module, you need to:

* Go to ``Connectors => [EasyPost] Backends``
* Configure one EasyPost backend per company you would like to use with

Usage
=====

Address Verification
--------------------

* Edit a partner in backend form view
* Click ``Validate`` button above street address
* Click ``Confirm`` button to validate address is correct, or ``Cancel`` to cancel

Note that the address change will be made immediately after hitting ``Confirm``,
regardless of whether you save the partner or not.

Rate Purchases
---------------
* Assign a ``Delivery Packaging`` to the Stock Picking and verify the weight
* Click the ``Additional Info`` tab under a Stock Picking to view the Rates.
* Click the green check button to purchase the rate.

Note that you can only purchase a rate after you have moved the picking out of
draft status.


Known Issues / Roadmap
======================

* Handle validation errors from addresses
* Some duplicate calls to EasyPost (Address, Shipment) - seems to be just in the tests though
* Add a default EasyPost connection to span all companies
* Mass address verification
* Label import operates in Shipment context, due to needing selected rate info not within PostageLabel
* Shipment buy workflow is a little ghetto with the intermediary wizard
* Logic to get package weight currently queries the parent stock.picking for this data

Credits
=======

Images
------

* LasLabs: `Icon <https://repo.laslabs.com/projects/TEM/repos/odoo-module_template/browse/module_name/static/description/icon.svg?raw>`_.

Contributors
------------

* Dave Lasley <dave@laslabs.com>
* Ted Salmon <tsalmon@laslabs.com>

Maintainer
----------

.. image:: https://laslabs.com/logo.png
   :alt: LasLabs Inc.
   :target: https://laslabs.com

This module is maintained by LasLabs Inc.
