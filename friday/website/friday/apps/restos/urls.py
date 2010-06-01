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
        r"^category/(?P<category>\w+)/$",
        view_restos_by_category,
        name="friday.view_restos_by_category"
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
        r"^(?P<resto_id>\d+)/$",
        view_resto,
        name="friday.view_resto"
    ),
    url(
        r"^(?P<resto_id>\d+)/tags/$",
        view_resto_tags,
        name="friday.view_resto_tags"
    ),
    url(
        r"^(?P<resto_id>\d+)/remove_tag/$",
        remove_resto_tag,
        name="friday.remove_resto_tag"
    ),
    url(
        r"^(?P<resto_id>\d+)/edit/$",
        edit_resto,
        name="friday.edit_resto"
    ),
    url(
        r"^(?P<resto_id>\d+)/delete/$",
        delete_resto,
        name="friday.delete_resto"
    ),
    url(
        r"^(?P<resto_id>\d+)/change_fave/$",
        change_resto_fave,
        name="friday.change_resto_fave"
    ),
    url(
        r"^(?P<resto_id>\d+)/recommend/$",
        recommend_dish,
        name="friday.recommend_dish"
    ),
    url(
        r"^(?P<resto_id>\d+)/(?P<dish_id>\d+)/change_fan/$",
        change_dish_fan,
        name="friday.change_dish_fan"
    ),
    url(
        r"^(?P<resto_id>\d+)/(?P<dish_id>\d+)/edit/$",
        edit_dish,
        name="friday.edit_dish"
    ),
    url(
        r"^(?P<resto_id>\d+)/(?P<dish_id>\d+)/delete/$",
        delete_dish,
        name="friday.delete_dish"
    ),
    url(
        r"^dish/$",
        search_dish,
        name="friday.search_dish"
    ),
)


# EOF
