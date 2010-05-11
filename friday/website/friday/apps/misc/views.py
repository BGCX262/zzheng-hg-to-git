#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

from friday.auth import users


def welcome(request):
    current_user = users.get_current_user(request)
    if current_user:
        redirect_url = reverse("friday.home")
        return HttpResponseRedirect(redirect_url)
    else:
        data = {}
        return render_to_response("misc/welcome.html", data, RequestContext(request))


def home(request):
    data = {}
    return render_to_response("misc/home.html", data, RequestContext(request))


def about(request, topic=None):
    _TOPICS = ("browser", "versions")
    if topic not in _TOPICS:
        template_file = "misc/about.html"
    else:
        template_file = "misc/about_%s.html" % topic
    data = {}
    return render_to_response(template_file, data, RequestContext(request))


def not_found(request):
    data = {"bad_url": request.path}
    return render_to_response("misc/not_found.html", data, RequestContext(request))


# EOF
