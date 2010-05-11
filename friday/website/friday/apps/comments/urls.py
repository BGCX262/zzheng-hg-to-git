#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-15.
# $Id$
#


from django.conf.urls.defaults import *
from friday.apps.comments.views import *


urlpatterns = patterns("",
    url(
        r"^(?P<ref_type>[\w\.\-]+)/(?P<ref_pk>[\w\.\-]+)/$",
        view_comments,
        name="friday.view_comments"
    ),
)


# EOF
