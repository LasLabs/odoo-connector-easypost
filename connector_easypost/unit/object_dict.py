# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

class ObjectDict(object):
    """ This class allows you to create objects with
    attributes and values direct from a `dict`. Useful
    when you have a dict that needs to be accessed like
    an object for compatibility """

    def __init__(self, **data):
        self.__dict__ = data

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, val):
        return setattr(self, key, val)

    def __repr__(self):
        return str(self.__dict__)
