#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-04-30.
# $Id$
#

"""
Script for handling incoming email.
"""

import os
os.environ["DJANGO_SETTINGS_MODULE"] = "friday.settings"

from djangomockup import bootstrap

import email
import logging
import re

from google.appengine.api.mail import InboundEmailMessage
from google.appengine.ext.webapp import WSGIApplication
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app

from friday.apps.poststats.signals import post_received


def _grab_emails(*args):
    pattern = re.compile(r"[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}")
    emails = set()
    for arg in args:
        if arg:
            emails.update(pattern.findall(str(arg)))
    return list(emails)


class IncomingEmailHandler(InboundMailHandler):

    def receive(self, mail_message):
        try:
            poster = _grab_emails(getattr(mail_message, "sender", None))
            logging.info("Received email from: %s" % poster)
            if len(poster) != 1:
                logging.warning("Suspicious sender of incoming email: %s" % poster)
                return
            poster = poster[0]
            to = getattr(mail_message, "to", None)
            cc = getattr(mail_message, "cc", None)
            recipients = _grab_emails(to, cc)
            post_received.send(
                sender=self.__class__,
                subject=getattr(mail_message, "subject", None),
                poster=poster,
                recipients=recipients
            )
        except Exception, exc:
            logging.error("Failed to handle incoming email: %s" % exc)
            logging.exception(exc)


def main():
    application = WSGIApplication([IncomingEmailHandler.mapping()], debug=True)
    run_wsgi_app(application)


if __name__ == "__main__":
    main()


# EOF
