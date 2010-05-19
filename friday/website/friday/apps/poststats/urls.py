#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

from django.conf.urls.defaults import *
from friday.apps.poststats.views import *


urlpatterns = patterns("",
    url(
        r"^group_post_stat/$",
        view_group_post_stat,
        name="friday.view_group_post_stat"
    ),
    url(
        r"^group_post_stat/(?P<year>\d{4})/(?P<month>\d{1,2})/$",
        view_group_post_stat,
        name="friday.view_group_post_stat"
    ),
)


# EOF
