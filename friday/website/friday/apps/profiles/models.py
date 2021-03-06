#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-20.
# $Id$
#

import datetime

from google.appengine.ext import db

from djangomockup import models
from friday.auth import users


class Profile(models.Model):

    GRAVATAR = "gravatar"
    IMAGE_URL = "image_url"

    user = db.ReferenceProperty(users.User, required=True)
    biography = db.TextProperty()
    tel = db.PhoneNumberProperty()
    website = db.LinkProperty()
    avatar_source = db.StringProperty(required=True, default=GRAVATAR)
    avatar_url = db.LinkProperty()

    schema_version = db.IntegerProperty(required=True, default=1)

    @property
    def username(self):
        return self.user.username

    @property
    def email(self):
        return self.user.email

    @property
    def join_date(self):
        return self.user.join_date

    def _get_name(self):
        return self.user.name
    def _set_name(self, value):
        self.user.name = value
    name = property(_get_name, _set_name)

    def _get_alt_email(self):
        return self.user.alt_email
    def _set_alt_email(self, value):
        self.user.alt_email = value
    alt_email = property(_get_alt_email, _set_alt_email)

    def __unicode__(self):
        return unicode(self.user)

    def save(self):
        self.user.save()
        return super(Profile, self).save()

    @classmethod
    def _make_pk(cls, user):
        return user.email.lower()

    @classmethod
    def get_unique(cls, user):
        pk = cls._make_pk(user)
        try:
            instance = cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            instance = None
        return instance

    @classmethod
    def create(cls, user, **kwargs):
        pk = cls._make_pk(user)
        name = kwargs.get("name")
        if "name" in kwargs:
            del kwargs["name"]
        alt_email = kwargs.get("alt_email")
        if "alt_email" in kwargs:
            del kwargs["alt_email"]
        instance = cls(key_name=pk, user=user, **kwargs)
        instance.name = name
        instance.alt_email = alt_email
        return instance

    @classmethod
    def find_all(cls, **kwargs):
        query = cls.objects.order_by(kwargs.get("order_by") or "user")
        if kwargs.get("limit"):
            query.set_limit(kwargs["limit"])
        return query


# EOF
