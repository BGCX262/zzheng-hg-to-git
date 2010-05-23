#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-04-29.
# $Id$
#

import logging

from django.conf import settings
from django.template.loader import render_to_string

from friday.auth import users
from friday.apps.notifications.signals import something_happened
from friday.apps.activities.models import Activity


def _render_message(template_name, data):
    template_file = "activities/mails/%s.txt" % template_name
    return render_to_string(template_file, data)


def activity_created(activity):
    # Do nothing if this group is not associated with a Google Group.
    google_group = activity.group.google_group or None
    if not google_group:
        logging.info("Group is not associated with a Google Group.")
        return
    # Otherwise, send a mail to the associated Google Group.
    _TEMPLATE_NAME = "activity_created"
    try:
        author = activity.submitter
        recipient = "%s@googlegroups.com" % google_group
        data = {
            "activity": activity,
            "http_host": getattr(settings, "MY_HTTP_HOST", None),
        }
        message = _render_message(_TEMPLATE_NAME, data)
        something_happened.send(
            sender=Activity.__name__,
            subject=None,
            message=message,
            author=author,
            recipients=[recipient]
        )
    except Exception, exc:
        logging.error("Failed to send notification for activity_created: %s" % exc)
        logging.exception(exc)


# EOF
