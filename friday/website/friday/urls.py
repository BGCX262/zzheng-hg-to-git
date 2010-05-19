#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

from django.conf.urls.defaults import *


urlpatterns = patterns("",

    (r"^admin/", include("friday.apps.admin.urls")),
    (r"^codeviewer/", include("friday.apps.codeviewer.urls")),
    (r"^comments/", include("friday.apps.comments.urls")),
    (r"^groups/", include("friday.apps.groups.urls")),
    (r"^groups/(?P<group_uid>\w+)/activities/", include("friday.apps.activities.urls")),
    (r"^groups/(?P<group_uid>\w+)/halloffame/", include("friday.apps.halloffame.urls")),
    (r"^groups/(?P<group_uid>\w+)/poststats/", include("friday.apps.poststats.urls")),
    (r"^notifications/", include("friday.apps.notifications.urls")),
    (r"^profiles/", include("friday.apps.profiles.urls")),
    (r"^restos/", include("friday.apps.restos.urls")),
    (r"^tagging/", include("friday.apps.tagging.urls")),
    (r"^", include("friday.apps.misc.urls")),

)


# EOF
