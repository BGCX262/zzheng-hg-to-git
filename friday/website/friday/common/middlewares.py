#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

import logging

from django.http import HttpRequest, HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response


class DummyMiddleware(object):

    def __init__(self):
        """Most middleware classes won't need an initializer since middleware classes are
        essentially placeholders for the process_* methods. If you do need some global state you
        may use __init__ to set up. However, keep in mind a couple of caveats:
         * Django initializes your middleware without any arguments, so you can't define __init__
           as requiring any arguments.
         * Unlike the process_* methods which get called once per request, __init__ gets called
           only once, when the web server starts up.
        """
        pass

    def process_request(self, request):
        """This function is called on each request, before Django decides which view to execute.
        This function should return either None or an HttpResponse object. If it returns None,
        Django will continue processing this request, executing any other middleware and, then,
        the appropriate view. If it returns an HttpResponse object, Django won't bother calling
        ANY other request, view or exception middleware, or the appropriate view; it'll return that
        HttpResponse. Response middleware is always called on every response.
        """
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        """This function is called just before Django calls the view. It should return either None
        or an HttpResponse object. If it returns None, Django will continue processing this
        request, executing any other process_view() middleware and, then, the appropriate view.
        If it returns an HttpResponse object, Django won't bother calling ANY other request, view
        or exception middleware, or the appropriate view; it'll return that HttpResponse. Response
        middleware is always called on every response.
        """
        return None

    def process_response(self, request, response):
        """This function should return an HttpResponse object. It could alter the given response,
        or it could create and return a brand-new HttpResponse.
        """
        return response

    def process_exception(self, request, exception):
        """This function is called when a view raises an exception. This function should return
        either None or an HttpResponse object. If it returns an HttpResponse object, the response
        will be returned to the browser. Otherwise, default exception handling kicks in.
        """
        return None


class RenderErrorMiddleware(object):

    ERROR_TEMPLATE = "error.html"

    def process_exception(self, request, exception):
        logging.error("Error occurred: %s - %s" % (type(exception), exception))
        if not isinstance(exception, Http404):
            logging.exception(exception)
        try:
            data = {"error": exception}
            return render_to_response(self.ERROR_TEMPLATE, data, RequestContext(request))
        except Exception, exc:
            logging.error("Failed to render error page: %s" % exc)
            logging.exception(exc)
            return None


# EOF
