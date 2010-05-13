#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

from django.conf.urls.defaults import *
from friday.apps.admin.views import *


urlpatterns = patterns("",
    url(
        r"^$",
        admin_home,
        name="friday.admin_home"
    ),
    url(
        r"^view_environ/$",
        view_environ,
        name="friday.view_environ"
    ),
    url(
        r"^import/members/$",
        import_members,
        name="friday.import_members"
    ),
    url(
        r"^import/restos/$",
        import_restos,
        name="friday.import_restos"
    ),
)


# EOF
