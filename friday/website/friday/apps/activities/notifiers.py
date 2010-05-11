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


_CATEGORY = Activity.__name__


def _render_message(template_name, data):
    template_file = "activities/notifications/%s.txt" % template_name
    return render_to_string(template_file, data)


def activity_created(activity):
    _TEMPLATE_NAME = "activity_created"
    try:
        author_email = getattr(settings, "MY_NOTIFICATION_AUTHOR", None)
        google_group = activity.group.google_group or None
        if not author_email:
            logging.info("Notification author is not defined in settings.")
        elif not google_group:
            logging.info("Group is not associated with a Google Group.")
        else:
            author = users.get_user(author_email)
            recipient = "%s@googlegroups.com" % google_group
            data = {
                "activity": activity,
                "http_host": getattr(settings, "MY_HTTP_HOST", None),
            }
            message = _render_message(_TEMPLATE_NAME, data)
            something_happened.send(
                sender=_CATEGORY,
                subject=None,
                message=message,
                author=author,
                recipients=[recipient]
            )
    except Exception, exc:
        logging.error("Failed to send notification for activity_created: %s" % exc)
        logging.exception(exc)


# EOF
