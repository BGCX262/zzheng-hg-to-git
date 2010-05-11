#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-05.
# $Id$
#

"""
Bootstrap script for running a Django (version 1.1) application on Google App Engine.

Notes:

* This module should be imported before any part of Django is imported.
* This module should be imported after the 'DJANGO_SETTINGS_MODULE' variable is set.

References:

* `Running Django on Google App Engine <http://code.google.com/appengine/articles/django.html>`_
* `Third-party Python Libraries on Google App Engine <http://code.google.com/appengine/docs/python/tools/libraries.html>`_

"""

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


#
# Done.
#
_bootstrap_done = True


# EOF
