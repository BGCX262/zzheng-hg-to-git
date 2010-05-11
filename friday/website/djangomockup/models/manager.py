#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-04-27.
# $Id$
#

from djangomockup.models.query import QuerySet


class Manager(object):
    """
    This class simulates the Django Manager interface, through which database query operations are
    provided to models. To each model class, a manager called objects is added.
    """

    def __init__(self, model):
        super(Manager, self).__init__()
        self.model = model

    def get(self, **kwargs):
        """
        Returns the instance by primary key. Expected keyword arguments are: 'pk' or 'id'.
        If no instance is found, this function raises model's DoesNotExist exception.
        """
        if len(kwargs) != 1:
            raise TypeError("get() takes 1 argument (%d given)" % len(kwargs))
        if "pk" in kwargs:
            instance = self.model.get_by_key_name(kwargs["pk"])
        elif "id" in kwargs:
            instance = self.model.get_by_id(kwargs["id"])
        else:
            raise TypeError("get() got an unexpected keyword argument '%s'" % kwargs.items()[0])
        if instance is None:
            raise self.model.DoesNotExist()
        return instance

    def get_query_set(self):
        return QuerySet(self.model)

    def all(self):
        return self.get_query_set()

    def filter(self, **kwargs):
        return self.get_query_set().filter(**kwargs)

    def order_by(self, *fields):
        return self.get_query_set().order_by(*fields)

    def count(self):
        return self.get_query_set().count()


# EOF
