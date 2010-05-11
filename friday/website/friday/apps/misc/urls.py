#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

from django.conf.urls.defaults import *
from friday.apps.misc.views import *


urlpatterns = patterns("",
    url(
        r"^$",
        welcome,
        name="friday.welcome"
    ),
    url(
        r"^home/$",
        home,
        name="friday.home"
    ),
    url(
        r"^about/$",
        about,
        name="friday.about"
    ),
    url(
        r"^about/(?P<topic>\w+)/$",
        about,
        name="friday.about"
    ),
    url(
        r"^.*/$",
        not_found,
        name="friday.not_found"
    ),
)

# EOF
