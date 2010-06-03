#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-21.
# $Id$
#

import datetime
import logging

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render_to_response
from django.core.exceptions import ImproperlyConfigured

from friday.auth import users
from friday.common.actions import Action
from friday.common.prompt import Prompt
from friday.apps.groups.models import Group
from friday.apps.poststats.models import GroupStat, PosterStat
from friday.apps.notifications.signals import something_happened


class CronJobsHome(Action):

    PAGE_URL_NAME = "friday.cron.cron_jobs_home"
    PAGE_TEMPLATE = "cronjobs/home.html"

    def get_page(self):
        data = {}
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class BaseCronAction(Action):

    PAGE_TEMPLATE = "cronjobs/cron_job.html"

    JOB_TITLE = None
    JOB_DESCRIPTION = None

    def get_job_title(self):
        return self.JOB_TITLE or self.__class__.__name__

    def get_job_description(self):
        return self.JOB_DESCRIPTION

    def check_cron(self):
        """
        Checks whether the incoming request is a cron request. This function firstly checks the
        request headers for AppEngine's cron key, to see if it's a scheduled cron request.
        If not present, it checks the request's GET dict to see if it's a manual cron request.

        According to Django's documentation, the header key "X-AppEngine-Cron" set by AppEngine's
        cron service will be converted to "HTTP_X_APPENGINE_CRON":

        Any HTTP headers in the request are converted to META keys by converting all characters to
        uppercase, replacing any hyphens with underscores and adding an HTTP_ prefix to the name.

        <http://docs.djangoproject.com/en/dev/ref/request-response/>

        Returns:
            A 2-tuple of bool (is_cron_request, is_scheduled).
        """

        _HEADER_CRON_KEY = "HTTP_X_APPENGINE_CRON"
        value = self.request.META.get(_HEADER_CRON_KEY)
        logging.info("Checking cron key in request headers: %s = %s" % (_HEADER_CRON_KEY, value))
        if value == "true":
            return True, True

        _GET_CRON_KEY = "cron_"
        value = self.request.GET.get(_GET_CRON_KEY)
        logging.info("Checking cron key in request GET dict: %s = %s" % (_GET_CRON_KEY, value))
        if value == "true":
            return True, False

        logging.info("The incoming request is not a cron request.")
        return False, False

    def get_page(self):
        is_cron_request, is_scheduled = self.check_cron()
        if is_cron_request:
            logging.info("About to run cron job %s..." % self.get_job_title())
            try:
                message = self.run_cron_job(is_scheduled)
                logging.info("Cron job %s done: %s" % (self.get_job_title(), message))
                prompt = Prompt(info=message)
            except Exception, exc:
                message = "Failed to run cron job %s: %s" % (self.get_job_title(), exc)
                logging.error(message)
                logging.exception(message)
                prompt = Prompt(error=message)
        else:
            prompt = None
        data = {
            "job_title": self.get_job_title(),
            "job_description": self.get_job_description(),
            "prompt": prompt,
        }
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def run_cron_job(self, is_scheduled):
        raise NotImplementedError("sub-class should implement run_cron_job()")


class SendTopPosters(BaseCronAction):

    PAGE_URL_NAME = "friday.cron.send_top_posters"

    FROM_EMAIL = getattr(settings, "DEFAULT_FROM_EMAIL", None)

    def run_cron_job(self, is_scheduled):
        # Ensure that the webapp is properly configured for this cron job.
        if not self.FROM_EMAIL:
            raise ImproperlyConfigured("DEFAULT_FROM_EMAIL not defined in settings.py")
        # If the job is scheduled, run only on the 1st day of month.
        if is_scheduled:
            today = datetime.date.today()
            if today.day != 1:
                message = "Nothing is done: %s is not the 1st day of month." % today.isoformat()
                return message
        # Send top posters to Google Groups.
        groups = [group for group in Group.find_all() if group.google_group]
        mail_sent = 0
        for group in groups:
            try:
                mail_sent += self._send_top_posters(group)
            except Exception, exc:
                logging.error("Failed to send top posters of group %s: %s" % (group.uid, exc))
                logging.exception(exc)
        message = "Top posters sent to %s groups." % mail_sent
        return message

    def _send_top_posters(self, group):
        group_stat = GroupStat.get_unique(group=group, date=datetime.date.today(), month_delta=-1)
        if not group_stat:
            return 0
        top_posters = PosterStat.find_by_group_stat(group_stat=group_stat, limit=3)
        if not top_posters:
            return 0
        data = {
            "group_stat": group_stat,
            "top_posters": top_posters,
            "http_host": getattr(settings, "MY_HTTP_HOST", None),
        }
        message = render_to_string("cronjobs/mails/top_posters.txt", data)
        author = users.get_user(self.FROM_EMAIL)
        recipient = "%s@googlegroups.com" % group.google_group
        something_happened.send(
            sender=Group.__name__,
            subject=None,
            message=message,
            author=author,
            recipients=[recipient]
        )
        return 1


#---------------------------------------------------------------------------------------------------


def cron_jobs_home(request):
    return CronJobsHome(request).process()


def send_top_posters(request):
    return SendTopPosters(request).process()


# EOF











