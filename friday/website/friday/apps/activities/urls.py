#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

from django.conf.urls.defaults import *
from friday.apps.activities.views import *


urlpatterns = patterns("",
    url(
        r"^$",
        view_all_activities,
        name="friday.view_all_activities"
    ),
    url(
        r"^upcoming/$",
        view_upcoming_activities,
        name="friday.view_upcoming_activities"
    ),
    url(
        r"^create/$",
        create_activity,
        name="friday.create_activity"
    ),
    url(
        r"^(?P<activity_id>\d+)/$",
        view_activity,
        name="friday.view_activity"
    ),
    url(
        r"^(?P<activity_id>\d+)/edit/$",
        edit_activity,
        name="friday.edit_activity"
    ),
    url(
        r"^(?P<activity_id>\d+)/delete/$",
        delete_activity,
        name="friday.delete_activity"
    ),
    url(
        r"^(?P<activity_id>\d+)/attenders/$",
        view_attenders,
        name="friday.view_attenders"
    ),
)


# EOF
