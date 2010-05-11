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

from google.appengine.api.mail import InboundEmailMessage
from google.appengine.ext.webapp import WSGIApplication
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app


class LogSenderHandler(InboundMailHandler):

    def receive(self, mail_message):
        logging.info("Type: %s" % type(mail_message))
        logging.info("Received a message from: " + mail_message.sender)


def main():
    application = WSGIApplication([LogSenderHandler.mapping()], debug=True)
    run_wsgi_app(application)


if __name__ == "__main__":
    main()


# EOF
