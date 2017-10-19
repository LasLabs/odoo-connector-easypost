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

* Install Python dependencies - ``pip install easypost``
* Look at ``oca_dependencies.txt`` in the root of this repo. Modules from
  these repos and branches are required for this module. The specific modules
  are listed in ``__manifest__.py``. See `here <https://github.com/OCA/
  maintainer-quality-tools/blob/master/sample_files/oca_dependencies.txt>`_ for
  more information regarding the syntax of the ``oca_dependencies.txt`` file.
* Install Easypost Connector module

Configuration
=============

To configure this module, you need to:

* Go to ``Connectors => [EasyPost] Backends``
* Configure one EasyPost backend per company you would like to use it with
* Restart Odoo (requirement of any new connector to set proper DB triggers)

If using multiple stock locations, you must make sure to assign the owner of
all warehouse stock locations (``warehouse.lot_stock_id``) in order for the
correct outbound address to be used.

Note that the ``weight`` and ``volume`` fields in your products must be accurrate.
If this is not the case, shipping estimations will be incorrect - particularly during
the sale phase.

Usage
=====

Predefined Packages
-------------------

* Predefined packages will automatically be added to Packaging options upon
  module install

Address Verification
--------------------

* Navigate to any partner
* Click the ``More`` or ``Actions`` menu (depending on Odoo version)
* Click ``Validate Address`` to trigger the address validation wizard

Rate Purchases
---------------

* Put products into a package
* Assign a packaging template to that package
* Click the ``Additional Info`` tab under a Stock Picking to view the Rates.
* Click the green check button to purchase the rate.

Note that you can only purchase a rate after you have moved the picking out of
draft status.

Known Issues / Roadmap
======================

* Handle validation errors from addresses
* Some duplicate calls to EasyPost (Address, Shipment) - seems to be just in
  the tests though
* Add a default EasyPost connection to span all companies
* Mass address verification
* Label import operates in Shipment context, due to needing selected rate info
  not within PostageLabel
* Only USPS service types are included by default. Everything else is created
  the first time rates are gathered.

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
* Ted Salmon <tsalmon@laslabs.com>

Maintainer
----------

.. image:: https://laslabs.com/logo.png
   :alt: LasLabs Inc.
   :target: https://laslabs.com

This module is maintained by LasLabs Inc.
