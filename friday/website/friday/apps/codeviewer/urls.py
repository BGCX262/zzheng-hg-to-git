#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-06.
# $Id$
#

from django.conf.urls.defaults import *
from friday.apps.codeviewer.views import *


urlpatterns = patterns("",
    url(
        r"^(?P<path>.*)$",
        view_code,
        name="friday.view_code"
    ),
)


# EOF
