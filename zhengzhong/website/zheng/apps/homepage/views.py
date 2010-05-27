#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2008 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2008-12-19.
# $Id$
#

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response


def home(request):
    return render_to_response("homepage/home.html", {}, RequestContext(request))


def about_java(request):
    return render_to_response("homepage/about_java.html", {}, RequestContext(request))


def not_found(request):
    data = {"bad_url": request.path,}
    response = render_to_response("homepage/not_found.html", data, RequestContext(request))
    response.status_code = 404  # not found.
    return response


# EOF
