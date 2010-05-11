#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-07.
# $Id$
#

import logging

from google.appengine.ext import db

from djangomockup import models


class User(models.Model):

    # key_name is user's email address.
    user = db.UserProperty(required=True)
    name = db.StringProperty()
    join_date = db.DateTimeProperty(required=True, auto_now_add=True)

    schema_version = db.IntegerProperty(required=True, default=1)

    def __unicode__(self):
        return unicode(self.name or self.user.nickname())

    def __nonzero__(self):
        return True

    @property
    def username(self):
        return self.user.nickname()

    @property
    def email(self):
        return self.user.email()

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    @classmethod
    def get_or_create(cls, google_user):
        email = google_user.email()
        try:
            user = cls.objects.get(pk=email)
        except cls.DoesNotExist:
            logging.info("Creating new user for '%s'." % email)
            user = cls(key_name=email, user=google_user)
            user.save()
        return user


class AnonymousUser(object):

    def __init__(self):
        super(AnonymousUser, self).__init__()
        self.username = None
        self.email = None

    def __unicode__(self):
        return "Anonymous"

    def __str__(self):
        return unicode(self).encode("utf-8")

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return 1  # instances always return the same hash value

    def __nonzero__(self):
        return False

    def save(self):
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()

    def is_anonymous(self):
        return True

    def is_authenticated(self):
        return False


# EOF