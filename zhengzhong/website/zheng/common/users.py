#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-07.
# $Id$
#

from __future__ import absolute_import  # PEP 328

import logging

from django.conf import settings
from google.appengine.api import users


__all__ = (
    "User",
    "get_current_user",
    "create_login_url",
    "create_logout_url",
    "get_user",
    "is_webmaster",
)


class User(object):

    def __init__(self, user):
        self._user = user

    def __unicode__(self):
        return unicode(self.username)

    def __str__(self):
        return unicode(self).encode("utf-8")

    def __nonzero__(self):
        return self._user is not None

    @property
    def username(self):
        if self._user is not None:
            return self._user.nickname()
        return None

    @property
    def email(self):
        if self._user is not None:
            return self._user.email()
        return None

    def is_anonymous(self):
        return self._user is None

    def is_authenticated(self):
        return self._user is not None


def get_current_user(request):
    google_user = users.get_current_user()
    return User(google_user)


def create_login_url(dest_url):
    return users.create_login_url(dest_url)


def create_logout_url(dest_url):
    return users.create_logout_url(dest_url)


def get_user(username):
    username = username.strip()
    if "@" in username:
        email = username
    else:
        email_domain = getattr(settings, "MY_EMAIL_DOMAIN")
        email = "%s@%s" % (username, email_domain)
    google_user = users.User(email)
    return User(google_user)


def is_webmaster(user):
    if not user:
        return False
    else:
        webmaster_emails = getattr(settings, "MY_WEBMASTER_EMAILS", ())
        return user.email in webmaster_emails


# EOF
