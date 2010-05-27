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

from zheng.common import users
from zheng.common.errors import ProgrammingError, BadRequestError


__all__ = ("Action", "WebmasterAction",)


class Action(object):

    PAGE_URL_NAME = None
    PAGE_TEMPLATE = None

    AJAX_URL_NAME = None
    AJAX_TEMPLATE = None

    def __init__(self, request):
        self._request = request

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def request(self):
        return self._request

    def get_page_template(self):
        return self.PAGE_TEMPLATE

    def get_ajax_template(self):
        return self.AJAX_TEMPLATE

    @property
    def current_user(self):
        return users.get_current_user(self.request)

    def process(self):
        is_ajax = self.request.is_ajax() or (self.request.REQUEST.get("ajax") == "ajax")
        if is_ajax:
            return self.process_ajax()
        else:
            return self.process_page()

    def process_ajax(self):
        if self.request.method == "GET":
            data = self.get_ajax()
        elif self.request.method == "POST":
            data = self.post_ajax()
        else:
            message = "%s does not support AJAX %s request." % (self.name, self.request.method)
            raise BadRequestError(self.request, message)
        data = self.update_data(data)
        return render_to_response(self.get_ajax_template(), data, RequestContext(self.request))

    def process_page(self):
        if self.request.method == "GET":
            return self.get_page()
        elif self.request.method == "POST":
            return self.post_page()
        else:
            message = "%s does not support %s request." % (self.name, self.request.method)
            raise BadRequestError(self.request, message)

    def update_data(self, data):
        return data

    def get_page(self):
        message = "%s does not support GET request." % self.name
        raise BadRequestError(self.request, message)

    def post_page(self):
        message = "%s does not support POST request." % self.name
        raise BadRequestError(self.request, message)

    def get_ajax(self):
        message = "%s does not support AJAX GET request." % self.name
        raise BadRequestError(self.request, message)

    def post_ajax(self):
        message = "%s does not support AJAX POST request." % self.name
        raise BadRequestError(self.request, message)

    @classmethod
    def get_page_url(cls, **kwargs):
        if not cls.PAGE_URL_NAME:
            message = "Failed to get page URL for %s: PAGE_URL_NAME not defined." % cls.__name__
            raise ProgrammingError(message)
        return reverse(cls.PAGE_URL_NAME, kwargs=kwargs)

    @classmethod
    def get_ajax_url(cls, **kwargs):
        if not cls.AJAX_URL_NAME:
            message = "Failed to get AJAX URL for %s: AJAX_URL_NAME not defined." % cls.__name__
            raise ProgrammingError(message)
        return reverse(cls.AJAX_URL_NAME, kwargs=kwargs)


class WebmasterAction(Action):

    def process(self):
        if not users.is_webmaster(self.current_user):
            message = "The action '%s' is restricted to webmasters." % self.name
            raise BadRequestError(self.request, message)
        else:
            return super(WebmasterAction, self).process()


# EOF
