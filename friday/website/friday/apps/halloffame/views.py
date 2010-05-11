#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-11.
# $Id$
#

import logging

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from friday.auth import users
from friday.common.errors import BadRequestError, EntityNotFoundError
from friday.common.prompt import Prompt

from friday.apps.groups.models import Group
from friday.apps.groups.views import BaseGroupAction
from friday.apps.halloffame.models import Inductee
from friday.apps.halloffame.forms import InducteeForm


class ViewHallOfFame(BaseGroupAction):

    PAGE_URL_NAME = "friday.view_hall_of_fame"
    PAGE_TEMPLATE = "halloffame/home.html"

    def get_page(self):
        data = {"inductees": Inductee.find_by_group(group=self.get_group())}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class AddInductee(BaseGroupAction):

    PAGE_URL_NAME = "friday.add_inductee"
    PAGE_TEMPLATE = "halloffame/add_inductee.html"

    def _check_create_access(self):
        if not users.is_webmaster(self.current_user):
            message = "Current user cannot add an inductee."
            raise BadRequestError(self.request, message)

    def get_page(self):
        self._check_create_access()
        data = {"inductee_form": InducteeForm()}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        self._check_create_access()
        inductee_form = InducteeForm(data=self.request.POST)
        try:
            inductee = inductee_form.create(group=self.get_group())
            message = "Inductee %s has been created successfully." % inductee.uid
            logging.info(message)
            redirect_url = ViewInductee.get_page_url(
                group_uid=self.group_uid,
                inductee_uid=inductee.uid
            )
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to create inductee in datastore: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"inductee_form": inductee_form, "prompt": Prompt(error=message)}
            data = self.update_data(data)
            return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class ViewInductee(BaseGroupAction):

    PAGE_URL_NAME = "friday.view_inductee"
    PAGE_TEMPLATE = "halloffame/view_inductee.html"

    def __init__(self, request, group_uid, inductee_uid):
        super(ViewInductee, self).__init__(request, group_uid)
        self.inductee_uid = inductee_uid

    def get_inductee(self):
        inductee = Inductee.get_unique(group=self.get_group(), uid=self.inductee_uid)
        if not inductee:
            message = "searched by inductee uid '%s'." % self.inductee_uid
            raise EntityNotFoundError(Inductee, message)
        return inductee

    def get_page(self):
        data = {"inductee": self.get_inductee()}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


#---------------------------------------------------------------------------------------------------


def view_hall_of_fame(request, group_uid):
    return ViewHallOfFame(request, group_uid).process()


def add_inductee(request, group_uid):
    return AddInductee(request, group_uid).process()


def view_inductee(request, group_uid, inductee_uid):
    return ViewInductee(request, group_uid, inductee_uid).process()


# EOF
