#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-05.
# $Id$
#

from google.appengine.ext import db


class QuerySet(object):
    """
    Wrapper class around Google App Engine's Query object to simulate Django's QuerySet.
    """

    _DEFAULT_LIMIT = 1000

    _OPERATORS = {
        "exact": "=",
        "in": "in",
        "gt": ">",
        "gte": ">=",
        "lt": "<",
        "lte": "<=",
    }

    _IMPLIED_OPERATOR = "="

    def __init__(self, model):
        super(QuerySet, self).__init__()
        self._query = db.Query(model)
        self._limit = self._DEFAULT_LIMIT
        self._cache = None

    def __nonzero__(self):
        if self._cache is not None:
            return bool(self._cache)
        return self._query.count(1) > 0

    def __iter__(self):
        if self._cache is None:
            self._cache = self._query.fetch(limit=self._limit)
        return self._cache.__iter__()

    def __getitem__(self, k):
        if not isinstance(k, slice):
            raise TypeError("[] got an invalid argument '%s': only slice is supported" % k)
        if k.start is not None or k.step is not None or k.stop is None:
            raise TypeError("[] got an invalid slice argument '%s': only stop is supported" % k)
        self._limit = int(k.stop)
        return self

    def filter(self, **kwargs):
        for name, value in kwargs.items():
            property_operator = self._parse_field_lookup("filter", name)
            self._query.filter(property_operator, value)
        return self

    def order_by(self, *fields):
        for field in fields:
            self._query.order(field)
        return self

    def count(self):
        return self._query.count(self._limit)

    def _parse_field_lookup(self, func, field_lookup):
        split_tuple = field_lookup.split("__")
        prop_name = split_tuple[0]
        if len(split_tuple) == 1:
            operator = self._IMPLIED_OPERATOR
        elif len(split_tuple) == 2:
            operator = self._OPERATORS.get(split_tuple[1])
        else:
            operator = None
        if not operator:
            raise TypeError("%s got an unexpected keyword argument '%s'" % (func, field_lookup))
        return "%s %s" % (prop_name, operator)


# EOF
