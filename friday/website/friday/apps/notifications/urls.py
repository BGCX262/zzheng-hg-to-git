#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-04-28.
# $Id$
#

from django.conf.urls.defaults import *
from friday.apps.notifications.views import *


urlpatterns = patterns("",
    url(
        r"^$",
        notifications_home,
        name="friday.notifications_home"
    ),
    url(
        r"^view/$",
        view_notifications,
        name="friday.view_notifications"
    ),
    url(
        r"^view/(?P<category>[\w\.\-]+)/$",
        view_notifications,
        name="friday.view_notifications"
    ),
    url(
        r"^send/$",
        send_notification,
        name="friday.send_notification"
    ),
    url(
        r"^(?P<notification_id>\d+)/$",
        view_notification,
        name="friday.view_notification"
    ),
)


# EOF
