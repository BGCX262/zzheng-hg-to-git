#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-21.
# $Id$
#

from django.conf.urls.defaults import *
from friday.apps.cronjobs.views import *


urlpatterns = patterns("",
    url(
        r"^$",
        cron_jobs_home,
        name="friday.cron.cron_jobs_home"
    ),
    url(
        r"^send_top_posters/$",
        send_top_posters,
        name="friday.cron.send_top_posters"
    ),
)


# EOF
