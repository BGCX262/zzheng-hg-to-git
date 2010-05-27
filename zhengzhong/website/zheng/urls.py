#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2008 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2008-04-28.
# $Id$
#

from django.conf.urls.defaults import *


urlpatterns = patterns("",
    (r"^", include("zheng.apps.homepage.urls")),
)


# EOF
