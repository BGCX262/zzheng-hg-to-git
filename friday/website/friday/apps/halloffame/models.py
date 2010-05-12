#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-11.
# $Id$
#

import logging

from google.appengine.ext import db

from djangomockup import models

from friday.auth import users
from friday.apps.groups.models import Group


class Inductee(models.Model):

    group = db.ReferenceProperty(Group, required=True)
    uid = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    user = db.ReferenceProperty(users.User)
    summary = db.StringProperty()
    biography = db.TextProperty(required=True)
    photo_type = db.StringProperty()
    photo_data = db.BlobProperty()
    inducted_date = db.DateProperty(required=True, auto_now_add=True)

    schema_version = db.IntegerProperty(required=True, default=1)

    def __unicode__(self):
        return unicode(self.name)

    @classmethod
    def _make_pk(cls, group, uid):
        return "%s/%s" % (group.uid, uid)

    @classmethod
    def create(cls, group, uid, **kwargs):
        pk = cls._make_pk(group, uid)
        return cls(key_name=pk, group=group, uid=uid, **kwargs)

    @classmethod
    def get_unique(cls, group, uid):
        pk = cls._make_pk(group, uid)
        try:
            instance = cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            instance = None
        return instance

    @classmethod
    def find_by_group(cls, group, **kwargs):
        query = cls.objects.filter(group=group)
        query = query.order_by(kwargs.get("order_by") or "-inducted_date")
        if kwargs.get("limit"):
            query = query[:kwargs["limit"]]
        return query


# EOF
