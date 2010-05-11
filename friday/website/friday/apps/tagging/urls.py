#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-04.
# $Id$
#

from django.conf.urls.defaults import *
from friday.apps.tagging.views import *


urlpatterns = patterns("",
    url(
        r"^$",
        view_tags,
        name="friday.view_tags"
    ),
    url(
        r"^category/(?P<category>\w+)/$",
        view_tags,
        name="friday.view_tags"
    ),
    url(
        r"^cloud/(?P<category>\w+)/$",
        view_tag_cloud,
        name="friday.view_tag_cloud"
    ),
)


# EOF
