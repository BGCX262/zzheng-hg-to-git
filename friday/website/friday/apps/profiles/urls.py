#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

from django.conf.urls.defaults import *
from friday.apps.profiles.views import *


urlpatterns = patterns("",
    url(
        r"^(?P<username>[\w\.\-@]+)/$",
        view_profile,
        name="friday.view_profile"
    ),
    url(
        r"^(?P<username>[\w\.\-@]+)/avatar/$",
        view_avatar,
        name="friday.view_avatar"
    ),
    url(
        r"^(?P<username>[\w\.\-@]+)/edit/$",
        edit_profile,
        name="friday.edit_profile"
    ),
    url(
        r"^(?P<username>[\w\.\-@]+)/avatar/$",
        view_avatar,
        name="friday.view_avatar"
    ),
    url(
        r"^(?P<username>[\w\.\-@]+)/avatar/edit/$",
        edit_avatar,
        name="friday.edit_avatar"
    ),
)


# EOF
