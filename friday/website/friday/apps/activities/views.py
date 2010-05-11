#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

import logging

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from friday.common.errors import BadRequestError, InvalidFormError, EntityNotFoundError
from friday.common.prompt import Prompt

from friday.apps.groups.models import Group, Member
from friday.apps.groups.views import BaseGroupAction
from friday.apps.activities.models import Activity, Attender
from friday.apps.activities.access import ActivityAccess
from friday.apps.activities.forms import ActivityForm
from friday.apps.activities.notifiers import activity_created


class ViewAllActivities(BaseGroupAction):

    PAGE_URL_NAME = "friday.view_all_activities"
    PAGE_TEMPLATE = "activities/view_all_activities.html"

    def get_page(self):
        data = {"activities": Activity.find_all(self.get_group())}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class ViewUpcomingActivities(BaseGroupAction):

    AJAX_URL_NAME = "friday.view_upcoming_activities"
    AJAX_TEMPLATE = "activities/common/activities.html"

    def get_ajax(self):
        return {"activities": Activity.find_upcoming(self.get_group())}


class CreateActivity(BaseGroupAction):

    PAGE_URL_NAME = "friday.create_activity"
    PAGE_TEMPLATE = "activities/create_activity.html"

    def _check_create_access(self):
        if not self.get_group_access().can_contribute():
            message = "Current user cannot create activity in group %s." % self.get_group().uid
            logging.error(message)
            raise BadRequestError(self.request, message)

    def get_page(self):
        self._check_create_access()
        data = {"activity_form": ActivityForm()}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        self._check_create_access()
        activity_form = ActivityForm(data=self.request.POST)
        try:
            activity = activity_form.create(group=self.get_group(), submitter=self.current_user)
            message = "Activity #%d has been created successfully." % activity.id
            logging.info(message)
            activity_created(activity)
            prompt = Prompt(info=message)
            redirect_url = ViewActivity.get_page_url(
                group_uid=self.get_group().uid,
                activity_id=activity.id
            )
            redirect_url += "?" + prompt.urlencode()
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to create activity in datastore: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"activity_form": activity_form, "prompt": Prompt(error=message)}
            data = self.update_data(data)
            return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class BaseActivityAction(BaseGroupAction):

    def __init__(self, request, group_uid, activity_id):
        super(BaseActivityAction, self).__init__(request, group_uid)
        self.activity_id = int(activity_id)

    def get_activity(self):
        activity = Activity.get_unique(id=self.activity_id, group=self.get_group())
        if not activity:
            message = "searched by activity ID #%s." % self.activity_id
            raise EntityNotFoundError(Activity, message)
        return activity

    def get_activity_access(self):
        return ActivityAccess(self.get_activity(), self.current_user)

    def update_data(self, data):
        data["activity"] = self.get_activity()
        data["activity_access"] = self.get_activity_access()
        return super(BaseActivityAction, self).update_data(data)


class ViewActivity(BaseActivityAction):

    PAGE_URL_NAME = "friday.view_activity"
    PAGE_TEMPLATE = "activities/view_activity.html"

    AJAX_URL_NAME = "friday.view_activity"
    AJAX_TEMPLATE = "activities/common/activity_details.html"

    def get_page(self):
        data = self.update_data({})
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class EditActivity(BaseActivityAction):

    PAGE_URL_NAME = "friday.edit_activity"
    PAGE_TEMPLATE = "activities/edit_activity.html"

    def _check_edit_access(self):
        if not self.get_activity_access().can_edit():
            message = "Current user cannot edit activity #%s." % self.get_activity().id
            logging.error(message)
            raise BadRequestError(self.request, message)

    def get_page(self):
        self._check_edit_access()
        activity_form = ActivityForm(instance=self.get_activity())
        data = {"activity_form": activity_form}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        self._check_edit_access()
        activity_form = ActivityForm(data=self.request.POST, instance=self.get_activity())
        try:
            activity = activity_form.update()
            message = "Activity #%s has been updated successfully." % activity.id
            logging.info(message)
            redirect_url = ViewActivity.get_page_url(
                group_uid=activity.group.uid,
                activity_id=activity.id
            )
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to update activity in datastore: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"activity_form": activity_form, "prompt": Prompt(error=message)}
            data = self.update_data(data)
            return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class DeleteActivity(BaseActivityAction):

    PAGE_URL_NAME = "friday.delete_activity"
    PAGE_TEMPLATE = "activities/delete_activity.html"

    def _check_delete_access(self):
        if not self.get_activity_access().can_delete():
            message = "Current user cannot delete activity #%s." % self.get_activity().id
            logging.error(message)
            raise BadRequestError(self.request, message)

    def get_page(self):
        self._check_delete_access()
        data = self.update_data({})
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        self._check_delete_access()
        try:
            activity = self.get_activity()
            activity_id = activity.id  # Activity instance has no 'id' attribute after deletion.
            activity.delete()
            message = "Activity #%s has been deleted successfully." % activity_id
            logging.info(message)
            redirect_url = ViewAllActivities.get_page_url(group_uid=self.get_group().uid)
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to delete activity in datastore: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"prompt": Prompt(error=message)}
            data = self.update_data(data)
            return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class ViewAttenders(BaseActivityAction):

    AJAX_TEMPLATE = "activities/common/attenders.html"

    def update_data(self, data):
        data["attenders"] = Attender.find_by_activity(self.get_activity())
        return super(ViewAttenders, self).update_data(data)

    def get_ajax(self):
        return {}

    def post_ajax(self):
        action = self.request.POST.get("action")
        if action == "join":
            self._join()
        elif action == "quit":
            self._quit()
        else:
            message = "Unsupported action '%s'." % action
            logging.error(message)
            raise BadRequestError(self.request, message)
        return {}

    def _join(self):
        if not self.get_activity_access().can_join():
            message = "Current user cannot join the activity."
            logging.error(message)
            raise BadRequestError(self.request, message)
        try:
            with_friends = int(self.request.POST.get("with_friends", 0))
        except (TypeError, ValueError):
            with_friends = 0
        attender = Attender.create(
            activity=self.get_activity(),
            user=self.current_user,
            with_friends=with_friends
        )
        attender.save()

    def _quit(self):
        if not self.get_activity_access().can_quit():
            message = "Current user cannot quit the activity."
            logging.error(message)
            raise BadRequestError(self.request, message)
        attender = Attender.get_unique(activity=self.get_activity(), user=self.current_user)
        if not attender:
            message = "Cannot find attender for current user."
            logging.error(message)
            raise BadRequestError(self.request, message)
        attender.delete()


#---------------------------------------------------------------------------------------------------


def view_all_activities(request, group_uid):
    return ViewAllActivities(request, group_uid).process()


def view_upcoming_activities(request, group_uid):
    return ViewUpcomingActivities(request, group_uid).process()


def create_activity(request, group_uid):
    return CreateActivity(request, group_uid).process()


def view_activity(request, group_uid, activity_id):
    return ViewActivity(request, group_uid, activity_id).process()


def edit_activity(request, group_uid, activity_id):
    return EditActivity(request, group_uid, activity_id).process()


def delete_activity(request, group_uid, activity_id):
    return DeleteActivity(request, group_uid, activity_id).process()


def view_attenders(request, group_uid, activity_id):
    return ViewAttenders(request, group_uid, activity_id).process()


# EOF
