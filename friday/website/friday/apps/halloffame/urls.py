#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-11.
# $Id$
#

from django.conf.urls.defaults import *
from friday.apps.halloffame.views import *


urlpatterns = patterns("",
    url(
        r"^$",
        view_hall_of_fame,
        name="friday.view_hall_of_fame"
    ),
    url(
        r"^add/$",
        add_inductee,
        name="friday.add_inductee"
    ),
    url(
        r"^(?P<inductee_uid>\w+)/$",
        view_inductee,
        name="friday.view_inductee"
    ),
)


# EOF
