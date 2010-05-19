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


class ViewGroupPostStat(BaseGroupAction):

    AJAX_URL_NAME = "friday.view_group_post_stat"
    AJAX_TEMPLATE = "poststats/common/group_post_stat.html"

    def __init__(self, request, group_uid, year=None, month=None):
        super(ViewGroupPostStat, self).__init__(request, group_uid)
        if year and month:
            self.date = datetime.date(year, month, 1)
        else:
            self.date = datetime.date.today()

    def get_ajax(self):
        google_group = self.get_group().google_group
        if google_group:
            group_post_stat = GroupPostStat.get_unique(google_group=google_group, date=self.date)
        else:
            group_post_stat = None
        return {"group_post_stat": group_post_stat}


#---------------------------------------------------------------------------------------------------


def view_group_post_stat(request, group_uid, year=None, month=None):
    return ViewGroupPostStat(request, group_uid, year, month).process()


# EOF
