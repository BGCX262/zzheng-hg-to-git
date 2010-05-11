#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

from django.conf.urls.defaults import *
from friday.apps.groups.views import *


urlpatterns = patterns("",
    url(
        r"^$",
        groups_home,
        name="friday.groups_home"
    ),
    url(
        r"^all/$",
        view_all_groups,
        name="friday.view_all_groups"
    ),
    url(
        r"^create/$",
        create_group,
        name="friday.create_group"
    ),
    url(
        r"^(?P<group_uid>\w+)/$",
        view_group,
        name="friday.view_group"
    ),
    url(
        r"^(?P<group_uid>\w+)/edit/$",
        edit_group,
        name="friday.edit_group"
    ),
    url(
        r"^(?P<group_uid>\w+)/prettify/$",
        prettify_group,
        name="friday.prettify_group"
    ),
    url(
        r"^(?P<group_uid>\w+)/join/$",
        join_group,
        name="friday.join_group"
    ),
    url(
        r"^(?P<group_uid>\w+)/members/$",
        view_members,
        name="friday.view_members"
    ),
    url(
        r"^(?P<group_uid>\w+)/review/(?P<username>[\w\.\-@]+)/$",
        review_member,
        name="friday.review_member"
    ),
    url(
        r"^(?P<group_uid>\w+)/member/(?P<username>[\w\.\-@]+)/$",
        edit_member,
        name="friday.edit_member"
    ),
)


# EOF
