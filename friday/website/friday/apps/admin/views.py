#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

import logging
import os
import sys
import urllib

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

from friday.common.actions import WebmasterAction
from friday.common.errors import BadRequestError, InvalidFormError
from friday.common.prompt import Prompt
from friday.apps.groups.models import Group, Member
from friday.apps.admin.forms import ImportMembersForm, ImportRestosForm


class AdminHome(WebmasterAction):

    PAGE_URL_NAME = "friday.admin_home"
    PAGE_TEMPLATE = "admin/home.html"

    def get_page(self):
        data = {}
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class ViewEnviron(WebmasterAction):

    PAGE_URL_NAME = "friday.view_environ"
    PAGE_TEMPLATE = "admin/view_environ.html"

    def get_page(self):
        django_settings = []
        for name in settings.get_all_members():
            if name != "get_all_members" and not name.startswith("_"):
                value = getattr(settings, name, None)
                django_settings.append("%s = %s" % (name, value))
        os_environ = ["%s = %s" % (key, value) for key, value in os.environ.items()]
        sys_path = sys.path
        cookies = ["%s = %s" % (key, value) for key, value in self.request.COOKIES.items()]
        request_meta = ["%s = %s" % (key, value) for key, value in self.request.META.items()]
        data = {
            "django_settings": django_settings,
            "os_environ": os_environ,
            "sys_path": sys_path,
            "cookies": cookies,
            "request_meta": request_meta,
        }
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class UpdateDatastore(WebmasterAction):

    PAGE_URL_NAME = "friday.update_datastore"
    PAGE_TEMPLATE = "admin/update_datastore.html"

    def get_page(self):
        data = {"message": self.request.GET.get("message")}
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        from friday.apps.comments.models import Comment
        all_comments = Comment.objects.all()
        succeeded, failed, ignored = 0, 0, 0
        for comment in all_comments:
            try:
                stripped_content = comment.content
                if len(stripped_content) != len(comment.content):
                    comment.content = stripped_content
                    comment.save()
                    succeeded += 1
                else:
                    ignored += 1
            except Exception, exc:
                logging.error("Failed to upgrade comments: %s" % exc)
                logging.exception(exc)
                failed += 1
        message = "Upgraded %s comments (%s failed, %s ignored)" % (succeeded, failed, ignored)
        logging.info(message)
        redirect_url = "%s?%s" % (self.request.path, urllib.urlencode({"message": message}))
        return HttpResponseRedirect(redirect_url)


class ImportMembers(WebmasterAction):

    PAGE_URL_NAME = "friday.import_members"
    PAGE_TEMPLATE = "admin/import_members.html"

    def get_page(self):
        data = {
            "prompt": Prompt(request=self.request),
            "import_members_form": ImportMembersForm(),
        }
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        import_members_form = ImportMembersForm(data=self.request.POST, files=self.request.FILES)
        try:
            imported, ignored, failed = issue = import_members_form.import_members()
            message = "Imported %s members, %s entries ignored, %s entries failed." \
                    % (imported, ignored, failed)
            logging.info(message)
            prompt = Prompt(info=message)
            redirect_url = "%s?%s" % (self.get_page_url(), prompt.urlencode())
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to import members: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"import_members_form": import_members_form}
            data = self.update_data(data)
            return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class ImportRestos(WebmasterAction):

    PAGE_URL_NAME = "friday.import_restos"
    PAGE_TEMPLATE = "admin/import_restos.html"

    def get_page(self):
        data = {
            "prompt": Prompt(request=self.request),
            "import_restos_form": ImportRestosForm(),
        }
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        import_restos_form = ImportRestosForm(data=self.request.POST, files=self.request.FILES)
        try:
            imported, ignored, failed = issue = import_restos_form.import_restos()
            message = "Imported %s restos, %s entries ignored, %s entries failed." \
                    % (imported, ignored, failed)
            logging.info(message)
            prompt = Prompt(info=message)
            redirect_url = "%s?%s" % (self.get_page_url(), prompt.urlencode())
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to import members: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"import_restos_form": import_restos_form}
            data = self.update_data(data)
            return render_to_response(self.get_page_template(), data, RequestContext(self.request))


#---------------------------------------------------------------------------------------------------


def admin_home(request):
    return AdminHome(request).process()


def view_environ(request):
    return ViewEnviron(request).process()


def update_datastore(request):
    return UpdateDatastore(request).process()


def import_members(request):
    return ImportMembers(request).process()


def import_restos(request):
    return ImportRestos(request).process()


# EOF
