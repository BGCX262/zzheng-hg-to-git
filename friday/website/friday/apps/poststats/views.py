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
from friday.apps.poststats.models import GroupStat, PosterStat


class ViewGroupStat(BaseGroupAction):

    PAGE_URL_NAME = "friday.view_group_stat"
    PAGE_TEMPLATE = "poststats/view_group_stat.html"

    def __init__(self, request, group_uid, year=None, month=None):
        super(ViewGroupStat, self).__init__(request, group_uid)
        if year and month:
            self.date = datetime.date(int(year), int(month), 1)
        else:
            self.date = datetime.date.today()

    def get_page(self):
        group_stat = GroupStat.get_unique(group=self.get_group(), date=self.date)
        if group_stat is not None:
            top_posters = PosterStat.find_by_group_stat(group_stat=group_stat, limit=10)
        else:
            top_posters = None
        data = {"group_stat": group_stat, "top_posters": top_posters}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class ViewTopPosters(BaseGroupAction):

    AJAX_URL_NAME = "friday.view_top_posters"
    AJAX_TEMPLATE = "poststats/common/top_posters.html"

    def get_ajax(self):
        group_stat = GroupStat.get_unique(group=self.get_group(), date=datetime.date.today())
        if group_stat is not None:
            top_posters = PosterStat.find_by_group_stat(group_stat=group_stat, limit=3)
        else:
            top_posters = None
        return {"group_stat": group_stat, "top_posters": top_posters}


#---------------------------------------------------------------------------------------------------


def view_group_stat(request, group_uid, year=None, month=None):
    return ViewGroupStat(request, group_uid, year, month).process()


def view_top_posters(request, group_uid):
    return ViewTopPosters(request, group_uid).process()


# EOF
