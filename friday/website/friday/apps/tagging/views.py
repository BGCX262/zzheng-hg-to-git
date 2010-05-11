#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-04.
# $Id$
#

import logging

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from friday.common.errors import BadRequestError
from friday.common.actions import Action
from friday.apps.tagging.models import Tag


class ViewTags(Action):

    PAGE_URL_NAME = "friday.view_tags"
    PAGE_TEMPLATE = "tagging/view_tags.html"

    def __init__(self, request, category=None):
        super(ViewTags, self).__init__(request)
        self.category = category

    def get_page(self):
        data = {"category": self.category, "tags": Tag.find(category=self.category)}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class ViewTagCloud(Action):

    AJAX_URL_NAME = "friday.view_tag_cloud"
    AJAX_TEMPLATE = "tagging/common/tag_cloud.html"

    def __init__(self, request, category):
        super(ViewTagCloud, self).__init__(request)
        self.category = category

    def get_ajax(self):
        return {"category": self.category, "tag_cloud": Tag.get_cloud(category=self.category)}


#---------------------------------------------------------------------------------------------------


def view_tags(request, category=None):
    return ViewTags(request, category).process()


def view_tag_cloud(request, category):
    return ViewTagCloud(request, category).process()


# EOF
