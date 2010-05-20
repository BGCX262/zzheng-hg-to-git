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
        r"^stats/$",
        view_group_post_stats,
        name="friday.view_group_post_stats"
    ),
    url(
        r"^top_posters/$",
        view_top_posters,
        name="friday.view_top_posters"
    ),
)


# EOF
