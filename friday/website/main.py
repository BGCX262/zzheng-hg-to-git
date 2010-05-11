#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-05.
# $Id$
#

import os
os.environ["DJANGO_SETTINGS_MODULE"] = "friday.settings"

from djangomockup import bootstrap

from django.core.handlers.wsgi import WSGIHandler
from google.appengine.ext.webapp.util import run_wsgi_app


def main():
    application = WSGIHandler()
    run_wsgi_app(application)


if __name__ == "__main__":
    main()


# EOF
