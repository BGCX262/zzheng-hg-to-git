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
from friday.apps.halloffame.forms import InducteeForm, InducteePhotoForm


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
                group_uid=inductee.group.uid,
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


class BaseInducteeAction(BaseGroupAction):

    def __init__(self, request, group_uid, inductee_uid):
        super(BaseInducteeAction, self).__init__(request, group_uid)
        self.inductee_uid = inductee_uid

    def get_inductee(self):
        inductee = Inductee.get_unique(group=self.get_group(), uid=self.inductee_uid)
        if not inductee:
            message = "searched by inductee uid '%s'." % self.inductee_uid
            raise EntityNotFoundError(Inductee, message)
        return inductee

    def update_data(self, data):
        data["inductee"] = self.get_inductee()
        return super(BaseInducteeAction, self).update_data(data)


class ViewInductee(BaseInducteeAction):

    PAGE_URL_NAME = "friday.view_inductee"
    PAGE_TEMPLATE = "halloffame/view_inductee.html"

    def get_page(self):
        data = self.update_data({})
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class EditInductee(BaseInducteeAction):

    PAGE_URL_NAME = "friday.edit_inductee"
    PAGE_TEMPLATE = "halloffame/edit_inductee.html"

    def _check_edit_access(self):
        if not users.is_webmaster(self.current_user):
            message = "Current user cannot edit inductee."
            raise BadRequestError(self.request, message)

    def get_page(self):
        self._check_edit_access()
        data = {"inductee_form": InducteeForm(instance=self.get_inductee())}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        self._check_edit_access()
        inductee_form = InducteeForm(data=self.request.POST, instance=self.get_inductee())
        try:
            inductee = inductee_form.update()
            message = "Inductee %s has been updated successfully." % inductee.uid
            logging.info(message)
            redirect_url = ViewInductee.get_page_url(
                group_uid=inductee.group.uid,
                inductee_uid=inductee.uid
            )
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to update inductee in datastore: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"inductee_form": inductee_form, "prompt": Prompt(error=message)}
            data = self.update_data(data)
            return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class ChangeInducteePhoto(BaseInducteeAction):

    PAGE_URL_NAME = "friday.change_inductee_photo"
    PAGE_TEMPLATE = "halloffame/change_inductee_photo.html"

    def _check_edit_access(self):
        if not users.is_webmaster(self.current_user):
            message = "Current user cannot change photo of inductee."
            raise BadRequestError(self.request, message)

    def get_page(self):
        self._check_edit_access()
        data = {"inductee_photo_form": InducteePhotoForm()}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        self._check_edit_access()
        inductee_photo_form = InducteePhotoForm(data=self.request.POST, files=self.request.FILES)
        try:
            inductee = inductee_photo_form.update(inductee=self.get_inductee())
            message = "Photo of inductee %s has been created successfully." % inductee.uid
            logging.info(message)
            redirect_url = ViewInductee.get_page_url(
                group_uid=self.group_uid,
                inductee_uid=inductee.uid
            )
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to update photo of inductee in datastore: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"inductee_photo_form": inductee_photo_form, "prompt": Prompt(error=message)}
            data = self.update_data(data)
            return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class ViewInducteePhoto(BaseInducteeAction):

    PAGE_URL_NAME = "friday.view_inductee_photo"

    def get_page(self):
        inductee = self.get_inductee()
        if not inductee.photo_type or not inductee.photo_data:
            message = "Inductee %s does not have a photo." % inductee.uid
            raise BadRequestError(self.request, message)
        return HttpResponse(inductee.photo_data, mimetype=inductee.photo_type)


#---------------------------------------------------------------------------------------------------


def view_hall_of_fame(request, group_uid):
    return ViewHallOfFame(request, group_uid).process()


def add_inductee(request, group_uid):
    return AddInductee(request, group_uid).process()


def view_inductee(request, group_uid, inductee_uid):
    return ViewInductee(request, group_uid, inductee_uid).process()


def edit_inductee(request, group_uid, inductee_uid):
    return EditInductee(request, group_uid, inductee_uid).process()


def change_inductee_photo(request, group_uid, inductee_uid):
    return ChangeInducteePhoto(request, group_uid, inductee_uid).process()


def view_inductee_photo(request, group_uid, inductee_uid):
    return ViewInducteePhoto(request, group_uid, inductee_uid).process()


# EOF
