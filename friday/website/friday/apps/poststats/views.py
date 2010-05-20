#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-19.
# $Id$
#

import datetime

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from friday.apps.groups.views import BaseGroupAction
from friday.apps.poststats.models import GroupPostStat, MemberPostStat


class ViewGroupPostStats(BaseGroupAction):

    PAGE_URL_NAME = "friday.view_group_post_stats"
    PAGE_TEMPLATE = "poststats/view_group_post_stats.html"

    def get_page(self):
        google_group = self.get_group().google_group
        if google_group:
            stats = GroupPostStat.find_by_google_group(google_group=google_group, limit=3)
        else:
            stats = None
        data = {"stats": stats}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class ViewTopPosters(BaseGroupAction):

    AJAX_URL_NAME = "friday.view_top_posters"
    AJAX_TEMPLATE = "poststats/common/top_posters.html"

    def get_ajax(self):
        google_group = self.get_group().google_group
        if google_group:
            stat = GroupPostStat.get_unique(google_group=google_group, date=datetime.date.today())
        else:
            stat = None
        return {"stat": stat}


#---------------------------------------------------------------------------------------------------


def view_group_post_stats(request, group_uid):
    return ViewGroupPostStats(request, group_uid).process()


def view_top_posters(request, group_uid):
    return ViewTopPosters(request, group_uid).process()


# EOF
