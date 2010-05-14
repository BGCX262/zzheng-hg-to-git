#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-04-28.
# $Id$
#

import logging

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

from friday.common.actions import WebmasterAction
from friday.common.errors import BadRequestError, EntityNotFoundError
from friday.common.prompt import Prompt
from friday.apps.notifications.models import Notification
from friday.apps.notifications.forms import NotificationForm


class ViewNotifications(WebmasterAction):

    PAGE_URL_NAME = "friday.view_notifications"
    PAGE_TEMPLATE = "notifications/view_notifications.html"

    def __init__(self, request, category=None):
        super(ViewNotifications, self).__init__(request)
        self.category = category

    def get_page(self):
        if self.category:
            kwargs = {"category": self.category}
        else:
            kwargs = {}
        notifications = Notification.find(**kwargs)
        data = {"category": self.category, "notifications": notifications}
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class ViewNotification(WebmasterAction):

    PAGE_URL_NAME = "friday.view_notification"
    PAGE_TEMPLATE = "notifications/view_notification.html"

    def __init__(self, request, notification_id):
        super(ViewNotification, self).__init__(request)
        self.notification_id = int(notification_id)

    def get_notification(self):
        notification = Notification.get_unique(id=self.notification_id)
        if not notification:
            message = "searched by notification ID %s." % self.notification_id
            raise EntityNotFoundError(Notification, message)
        return notification

    def get_page(self):
        data = {"notification": self.get_notification()}
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class SendNotification(WebmasterAction):

    PAGE_URL_NAME = "friday.send_notification"
    PAGE_TEMPLATE = "notifications/send_notification.html"

    def get_page(self):
        data = {"notification_form": NotificationForm()}
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        notification_form = NotificationForm(data=self.request.POST)
        try:
            notification = notification_form.send(self.current_user)
            message = "Notification %s has been sent successfully." % notification.id
            logging.info(message)
            redirect_url = ViewNotification.get_page_url(notification_id=notification.id)
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to send mail: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"notification_form": notification_form, "prompt": Prompt(error=message)}
            data = self.update_data(data)
            return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class DeleteNotifications(WebmasterAction):

    PAGE_URL_NAME = "friday.delete_notifications"

    def post_page(self):
        notification_id_list = self.request.POST.getlist("notification_id")
        deleted, failed = 0, 0
        for notification_id in notification_id_list:
            try:
                notification = Notification.get_unique(id=int(notification_id))
                if not notification:
                    message = "searched by notification ID %s." % notification_id
                    raise EntityNotFoundError(Notification, message)
                notification.delete()
                deleted += 1
            except Exception, exc:
                message = "Failed to delete notification %s: %s" % (notification_id, exc)
                logging.error(message)
                logging.exception(exc)
                failed += 1
        if deleted + failed > 0:
            logging.info("Deleted %s notifications (%s failed)." % (deleted, failed))
        redirect_url = ViewNotifications.get_page_url()
        return HttpResponseRedirect(redirect_url)


#---------------------------------------------------------------------------------------------------


def notifications_home(request):
    return ViewNotifications(request).process()


def view_notifications(request, category=None):
    return ViewNotifications(request, category).process()


def view_notification(request, notification_id):
    return ViewNotification(request, notification_id).process()


def send_notification(request):
    return SendNotification(request).process()


def delete_notifications(request):
    return DeleteNotifications(request).process()


# EOF
