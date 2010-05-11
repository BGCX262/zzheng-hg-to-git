#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

import datetime

from google.appengine.ext import db

from djangomockup import models
from friday.auth import users
from friday.common.dbutils import filter_key


class Group(models.Model):

    _RESERVED_KEYS = ("create",)

    uid = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    slogan = db.StringProperty()
    description = db.TextProperty()
    website = db.LinkProperty()
    google_group = db.StringProperty()

    background_url = db.LinkProperty()
    logo_icon_url = db.LinkProperty()

    creator = db.ReferenceProperty(users.User, required=True, collection_name="created_groups")
    create_date = db.DateProperty(required=True)
    owner = db.ReferenceProperty(users.User, required=True, collection_name="owned_groups")
    own_date = db.DateProperty(required=True)

    schema_version = db.IntegerProperty(required=True, default=1)

    def __unicode__(self):
        return unicode(self.name)

    @property
    def members(self):
        return Member.find_by_group(group=self)

    @property
    def pending_members(self):
        return Member.find_by_group(group=self, is_approved=False)

    @classmethod
    def _make_pk(cls, uid):
        return filter_key(uid, reserved=cls._RESERVED_KEYS)

    @classmethod
    def get_unique(cls, uid):
        pk = cls._make_pk(uid)
        try:
            instance = cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            instance = None
        return instance

    @classmethod
    def create(cls, uid, creator, **kwargs):
        pk = cls._make_pk(uid)
        if kwargs.get("create_date"):
            create_date = kwargs["create_date"]
            del kwargs["create_date"]
        else:
            create_date = datetime.date.today()
        return cls(
            key_name=pk,
            uid=pk,
            creator=creator,
            create_date=create_date,
            owner=creator,
            own_date=create_date,
            **kwargs
        )

    @classmethod
    def find_all(cls, **kwargs):
        query = cls.objects.order_by(kwargs.get("order_by") or "-create_date")
        if kwargs.get("limit"):
            query = query[:kwargs["limit"]]
        return query


class Member(models.Model):

    ADMINISTRATOR = "administrator"
    MODERATOR = "moderator"
    MEMBER = "member"

    group = db.ReferenceProperty(reference_class=Group, required=True)
    user = db.ReferenceProperty(users.User, required=True)
    role = db.StringProperty(required=True, default=MEMBER)
    join_date = db.DateProperty(required=True)
    request_message = db.TextProperty()
    is_approved = db.BooleanProperty(required=True, default=False)
    is_emeritus = db.BooleanProperty(required=True, default=False)

    schema_version = db.IntegerProperty(required=True, default=1)

    @property
    def username(self):
        return self.user.username

    @property
    def email(self):
        return self.user.email

    def __unicode__(self):
        return unicode(self.user)

    @classmethod
    def _make_pk(cls, group, user):
        return "%s/%s" % (group.uid, user.email)

    @classmethod
    def create(cls, group, user, **kwargs):
        pk = cls._make_pk(group, user)
        if "join_date" not in kwargs:
            kwargs["join_date"] = datetime.date.today()
        return cls(key_name=pk, group=group, user=user, **kwargs)

    @classmethod
    def get_unique(cls, group, user):
        pk = cls._make_pk(group, user)
        try:
            instance = cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            instance = None
        return instance

    @classmethod
    def find_by_group(cls, group, is_approved=True, **kwargs):
        query = cls.objects.filter(group=group, is_approved=is_approved)
        if kwargs.get("order_by"):
            query = query.order_by(kwargs.get("order_by"))
        return query

    @classmethod
    def find_by_user(cls, user, **kwargs):
        query = cls.objects.filter(user=user)
        if kwargs.get("order_by"):
            query = query.order_by(kwargs.get("order_by"))
        return query


# EOF
