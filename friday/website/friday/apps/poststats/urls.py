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
        r"^stat/$",
        view_group_stat,
        name="friday.view_group_stat"
    ),
    url(
        r"^stat/(?P<year>\d{4})/(?P<month>\d{1,2})/$",
        view_group_stat,
        name="friday.view_group_stat"
    ),
    url(
        r"^top_posters/$",
        view_top_posters,
        name="friday.view_top_posters"
    ),
)


# EOF
