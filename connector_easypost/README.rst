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
* Install ``stock_delivery_label_new`` from https://github.com/laslabs/odoo-stock.git
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


Known Issues / Roadmap
======================

* Handle validation errors from addresses
* Some duplicate calls to EasyPost (Address, Shipment) - seems to be just in the tests though
* Add a default EasyPost connection to span all companies
* Mass address verification
* Label import operates in Shipment context, due to needing selected rate info not within PostageLabel
* Shipment buy workflow is a little ghetto with the intermediary wizard

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/laslabs/odoo-connector-easypost/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
please help us smash it by providing a detailed and welcomed feedback.


Credits
=======

Images
------

* LasLabs: `Icon <https://repo.laslabs.com/projects/TEM/repos/odoo-module_template/browse/module_name/static/description/icon.svg?raw>`_.

Contributors
------------

* Dave Lasley <dave@laslabs.com>

Maintainer
----------

.. image:: https://laslabs.com/logo.png
   :alt: LasLabs Inc.
   :target: https://laslabs.com

This module is maintained by LasLabs Inc.
