#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

import datetime
import logging
import os
import sys
import urllib

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

from friday.auth import users
from friday.common.actions import WebmasterAction
from friday.common.errors import BadRequestError, InvalidFormError
from friday.common.prompt import Prompt
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

        from friday.apps.groups.models import Group
        from friday.apps.poststats.models import GroupStat, PosterStat

        monthly_stats = (
            (datetime.date(2010, 1, 1), 342),
            (datetime.date(2010, 2, 1), 822),
            (datetime.date(2010, 3, 1), 315),
            (datetime.date(2010, 4, 1), 575),
        )
        group = Group.get_unique(uid="vivelevendredi")
        if group is None:
            message = "Fail to find group vivelevendredi."
            logging.error(message)
            raise BadRequestError(self.request, message)
        for date, post_count in monthly_stats:
            group_stat = GroupStat.get_or_create(group=group, date=date)
            group_stat.post_count = post_count
            group_stat.save()

        group_stat = GroupStat.get_or_create(group=group, date=datetime.date(2010, 5, 1))
        group_stat.post_count = 726
        group_stat.save()

        poster_stat = PosterStat.get_or_create(group_stat=group_stat, poster=users.get_user("xianlin.cao"))
        poster_stat.post_count = 129
        poster_stat.save()

        poster_stat = PosterStat.get_or_create(group_stat=group_stat, poster=users.get_user("chentianfan"))
        poster_stat.post_count = 87
        poster_stat.save()

        poster_stat = PosterStat.get_or_create(group_stat=group_stat, poster=users.get_user("dtownboy"))
        poster_stat.post_count = 65
        poster_stat.save()

        message = "Done."
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
