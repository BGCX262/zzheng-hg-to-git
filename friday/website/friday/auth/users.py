#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-07.
# $Id$
#

from __future__ import absolute_import  # PEP 328

from django.conf import settings
from google.appengine.api import users

from friday.auth.models import User, AnonymousUser


__all__ = (
    "User",
    "AnonymousUser",
    "get_current_user",
    "create_login_url",
    "create_logout_url",
    "get_user",
    "is_webmaster",
)


def get_current_user(request):
    google_user = users.get_current_user()
    if not google_user:
        return AnonymousUser()
    else:
        return User.get_or_create(google_user)


def create_login_url(dest_url):
    return users.create_login_url(dest_url)


def create_logout_url(dest_url):
    return users.create_logout_url(dest_url)


def get_user(username_or_email, create=True):
    username_or_email = username_or_email.strip()
    if "@" in username_or_email:
        email = username_or_email
    else:
        email_domain = getattr(settings, "MY_EMAIL_DOMAIN")
        email = "%s@%s" % (username_or_email, email_domain)
    google_user = users.User(email)
    if create:
        return User.get_or_create(google_user)
    else:
        return User.get_unique(google_user)


def get_user_by_email(email):
    email = email.strip()
    user = get_user(email, create=False)
    if user is not None:
        return user
    users = User.find_by_alt_email(email)
    if users:
        return users[0]
    else:
        return None


def is_webmaster(user):
    if not user:
        return False
    else:
        webmaster_emails = getattr(settings, "MY_WEBMASTER_EMAILS", ())
        return user.email in webmaster_emails


# EOF
