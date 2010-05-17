#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-05.
# $Id$
#

from google.appengine.ext import db


class QueryAlreadyExecuted(Exception):
    """
    When user tries to filter the query while the query has already been executed.
    """
    pass


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
        self._fill_cache()
        return bool(self._cache)

    def __len__(self):
        self._fill_cache()
        return len(self._cache)

    def __iter__(self):
        self._fill_cache()
        return self._cache.__iter__()

    def __getitem__(self, k):
        if not isinstance(k, (slice, int, long)):
            raise TypeError("list indices must be integers")
        self._fill_cache()
        return self._cache[k]

    def cursor(self):
        """
        Attention: this function is specific to Google App Engine.
        """
        self._fill_cache()
        if len(self._cache) < self._limit:
            return None
        return self._query.cursor()

    def with_cursor(self, cursor):
        """
        Attention: this function is specific to Google App Engine.
        """
        self._ensure_query_not_executed("with_cursor")
        if cursor:
            # We must convert the cursor to str, otherwise, we'll get a BadValueError:
            # Invalid cursor XXX: character mapping must return integer, None or unicode.
            self._query.with_cursor(str(cursor))
        return self

    def filter(self, **kwargs):
        self._ensure_query_not_executed("filter")
        for name, value in kwargs.items():
            property_operator = self._parse_field_lookup("filter", name)
            self._query.filter(property_operator, value)
        return self

    def order_by(self, *fields):
        self._ensure_query_not_executed("order_by")
        for field in fields:
            self._query.order(field)
        return self

    def set_limit(self, limit):
        self._ensure_query_not_executed("set_limit")
        self._limit = limit
        return self

    def count(self):
        self._fill_cache()
        return len(self._cache)

    def _fill_cache(self):
        if self._cache is None:
            self._cache = self._query.fetch(limit=self._limit)

    def _ensure_query_not_executed(self, operation_to_apply):
        if self._cache is not None:
            raise QueryAlreadyExecuted("Failed to apply %s on query set." % operation_to_apply)

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
