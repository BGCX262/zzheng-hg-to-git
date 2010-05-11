#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

from django.conf.urls.defaults import *
from friday.apps.restos.views import *


urlpatterns = patterns("",
    url(
        r"^$",
        restos_home,
        name="friday.restos_home"
    ),
    url(
        r"^all/$",
        view_all_restos,
        name="friday.view_all_restos"
    ),
    url(
        r"^tag_cloud/$",
        view_resto_tag_cloud,
        name="friday.view_resto_tag_cloud"
    ),
    url(
        r"^tag/$",
        view_restos_by_tag,
        name="friday.view_restos_by_tag"
    ),
    url(
        r"^create/$",
        create_resto,
        name="friday.create_resto"
    ),
    url(
        r"^(?P<resto_uid>\w+)/$",
        view_resto,
        name="friday.view_resto"
    ),
    url(
        r"^(?P<resto_uid>\w+)/tags/$",
        view_resto_tags,
        name="friday.view_resto_tags"
    ),
    url(
        r"^(?P<resto_uid>\w+)/remove_tag/$",
        remove_resto_tag,
        name="friday.remove_resto_tag"
    ),
    url(
        r"^(?P<resto_uid>\w+)/edit/$",
        edit_resto,
        name="friday.edit_resto"
    ),
    url(
        r"^(?P<resto_uid>\w+)/(?P<dish_id>\d+)/like_or_unlike/$",
        like_or_unlike_dish,
        name="friday.like_or_unlike_dish"
    ),
    url(
        r"^(?P<resto_uid>\w+)/edit_dishes/$",
        edit_dishes,
        name="friday.edit_dishes"
    ),
)


# EOF
