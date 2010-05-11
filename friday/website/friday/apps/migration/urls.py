#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-03.
# $Id$
#

from django.conf.urls.defaults import *
from friday.apps.migration.views import *


urlpatterns = patterns("",
    url(
        r"^$",
        migrate_model,
        name="friday.migrate_model"
    ),
)


# EOF
