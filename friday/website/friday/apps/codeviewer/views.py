#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-06.
# $Id$
#

import logging
import mimetypes
import os

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from friday.common.actions import WebmasterAction
from friday.common.errors import ProgrammingError


_ROOT_DIR = getattr(settings, "MY_ROOT_DIR", None)

_IGNORE = (".pyc",)


#---------------------------------------------------------------------------------------------------


class Entry(object):

    def __init__(self, path):
        super(Entry, self).__init__()
        self.path = path.strip("/") or None
        if self.path:
            self.name = os.path.basename(self.path)
            self.abs_path = os.path.normpath(os.path.join(_ROOT_DIR, path))
        else:
            self.name = ""
            self.abs_path = _ROOT_DIR
        self._content = None

    @property
    def exists(self):
        return os.path.exists(self.abs_path)

    @property
    def is_file(self):
        return os.path.isfile(self.abs_path)

    @property
    def is_dir(self):
        return os.path.isdir(self.abs_path)

    @property
    def mimetype(self):
        if not os.path.isfile(self.abs_path):
            return None
        else:
            ext = os.path.splitext(self.abs_path)[1].lower()
            if ext in (".yaml",):
                return "text/plain"
            else:
                return mimetypes.guess_type(self.abs_path, strict=False)[0]

    @property
    def is_text_file(self):
        mimetype = self.mimetype
        return mimetype is not None and mimetype.startswith("text/")

    @property
    def parents(self):
        parents = []
        if self.path:
            parent_path = os.path.split(self.path)[0]
            while parent_path:
                parents.append(Entry(parent_path))
                parent_path = os.path.split(parent_path)[0]
        parents.reverse()
        return parents

    @property
    def size(self):
        try:
            size = os.path.getsize(self.abs_path)
        except os.error:
            size = None
        return size

    @property
    def content(self):
        if self._content is not None:
            return self._content
        if self._content is None and os.path.isfile(self.abs_path):
            f = open(self.abs_path, "r")
            try:
                self._content = f.read()
            except Exception, exc:
                logging.error("Failed to read file %s: %s" % (self.abs_path, exc))
                logging.exception(exc)
                self._content = ""
            finally:
                f.close()
        return self._content

    @property
    def children(self):
        children = []
        if os.path.isdir(self.abs_path):
            for name in os.listdir(self.abs_path):
                ext = os.path.splitext(name)[1].lower()
                if ext not in _IGNORE:
                    if self.path:
                        child_path = "%s/%s" % (self.path, name)
                    else:
                        child_path = name
                    children.append(Entry(child_path))
        return children


#---------------------------------------------------------------------------------------------------


class ViewCode(WebmasterAction):

    PAGE_URL_NAME = "friday.view_code"
    PAGE_TEMPLATE = "codeviewer/view_code.html"

    def __init__(self, request, path=None):
        super(ViewCode, self).__init__(request)
        self.path = path or ""

    def get_page(self):
        if not _ROOT_DIR:
            message = "MY_ROOT_DIR not defined in settings.py"
            raise ProgrammingError(message)
        entry = Entry(self.path)
        if self.request.GET.get("download"):
            content = entry.content
            if content is not None:
                return HttpResponse(content, mimetype=entry.mimetype)
        data = {"entry": entry}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


#---------------------------------------------------------------------------------------------------


def view_code(request, path=None):
    return ViewCode(request, path).process()


# EOF
