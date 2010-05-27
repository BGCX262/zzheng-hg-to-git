#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2008 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2008-12-19.
# $Id$
#

from django.conf.urls.defaults import *
from zheng.apps.homepage.views import *


urlpatterns = patterns("",
    url(
        r"^$",
        home,
        name="zheng.home"
    ),
    url(
        r"^java/$",
        about_java,
        name="zheng.about_java"
    ),
    url(
        r"^.*/$",
        not_found,
        name="zheng.not_found"
    ),
)


# EOF
