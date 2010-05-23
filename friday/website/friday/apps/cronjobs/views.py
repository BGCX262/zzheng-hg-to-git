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
from friday.apps.poststats.models import GroupPostStat
from friday.apps.notifications.signals import something_happened


class BaseCronAction(Action):

    PAGE_TEMPLATE = "cronjobs/cron_job.html"

    JOB_TITLE = None
    JOB_DESCRIPTION = None

    CRON_HEADER = "X-AppEngine-Cron"
    CRON_PARAM = "cron_"

    def get_job_title(self):
        return self.JOB_TITLE or self.__class__.__name__

    def get_job_description(self):
        return self.JOB_DESCRIPTION

    def is_cron(self):
        value = self.request.META.get(self.CRON_HEADER) \
             or self.request.REQUEST.get(self.CRON_PARAM)
        return (value == "true")

    def get_page(self):
        prompt = None
        if self.is_cron():
            logging.info("About to run cron job %s..." % self.get_job_title())
            try:
                message = self.run_cron_job()
                logging.info("Cron job %s done: %s" % (self.get_job_title(), message))
                prompt = Prompt(info=message)
            except Exception, exc:
                message = "Failed to run cron job %s: %s" % (self.get_job_title(), exc)
                logging.error(message)
                logging.exception(message)
                prompt = Prompt(error=message)
        data = {
            "job_title": self.get_job_title(),
            "job_description": self.get_job_description(),
            "prompt": prompt,
        }
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def run_cron_job(self):
        raise NotImplementedError("sub-class should implement run_cron_job()")


class CronJobsHome(Action):

    PAGE_URL_NAME = "friday.cron.cron_jobs_home"
    PAGE_TEMPLATE = "cronjobs/home.html"

    def get_page(self):
        data = {}
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class SendTopPosters(BaseCronAction):

    PAGE_URL_NAME = "friday.cron.send_top_posters"

    _FROM_EMAIL = getattr(settings, "DEFAULT_FROM_EMAIL", None)

    def run_cron_job(self):
        today = datetime.date.today()
        if today.day != 1:
            message = "Nothing is done since %s is not the 1st day of month." % today.isoformat()
            return message
        if not self._FROM_EMAIL:
            raise ImproperlyConfigured("DEFAULT_FROM_EMAIL not defined in settings.py")
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
        group_post_stat = GroupPostStat.get_unique(
            google_group=group.google_group,
            date=datetime.date.today(),
            month_delta=-1
        )
        if not group_post_stat:
            return 0
        top_posters = group_post_stat.get_top_posters(5)
        if not top_posters:
            return 0
        data = {
            "group": group,
            "group_post_stat": group_post_stat,
            "top_posters": top_posters,
            "http_host": getattr(settings, "MY_HTTP_HOST", None),
        }
        message = render_to_string("cronjobs/mails/top_posters.txt", data)
        author = users.get_user(self._FROM_EMAIL)
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











