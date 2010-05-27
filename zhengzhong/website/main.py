#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-05.
# $Id$
#

#
# Set DJANGO_SETTINGS_MODULE variable.
#
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "zheng.settings"


#
# Select Django version.
#
from google.appengine.dist import use_library
use_library("django", "1.1")


#
# Force Django to reload its settings.
#
from django.conf import settings
settings._target = None


#
# Update Django signal handlers (for Django version 1.1).
#
import logging
import django.db
from django.core.signals import got_request_exception

def log_exception(*args, **kwds):
    logging.exception("Exception in request:")

got_request_exception.disconnect(django.db._rollback_on_exception)
got_request_exception.connect(log_exception)


#---------------------------------------------------------------------------------------------------


from django.core.handlers.wsgi import WSGIHandler
from google.appengine.ext.webapp.util import run_wsgi_app


def main():
    application = WSGIHandler()
    run_wsgi_app(application)


if __name__ == "__main__":
    main()


# EOF
