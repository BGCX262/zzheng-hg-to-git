#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-09.
# $Id$
#

import datetime
from platform import python_version

from django import get_version as django_version
from django.conf import settings
from django.http import HttpRequest

from friday import get_version as website_version
from friday.auth import users
from friday.common.browsers import Browser


_GOOGLE_AJAX_API_KEYS = {
    "www.zhengzhong.net": "ABQIAAAA6SC56e9JfGUas7BsUDqyuBQTYCh4nfnZskh9tX3CKbKESYY0QBQRDfWUx_P2DPVUCiFC7DmMx_qv6A",
}


def common_data_processor(request):
    server_name = request.META.get("SERVER_NAME")
    google_ajax_api_key = _GOOGLE_AJAX_API_KEYS.get(server_name, "")
    return {
        "site_name_": getattr(settings, "MY_SITE_NAME", None),
        "static_": getattr(settings, "MY_STATIC_URL_PREFIX", ""),
        "browser_": Browser(request.META.get("HTTP_USER_AGENT")),
        "server_name_": server_name,
        "google_ajax_api_key_": google_ajax_api_key,
        "today_": datetime.date.today(),
    }


def current_user_processor(request):
    user = users.get_current_user(request)
    if not user:
        login_url = users.create_login_url(request.path)
        logout_url = None
    else:
        login_url = None
        logout_url = users.create_logout_url(request.path)
    return {
        "user_": user,
        "user_ip_": request.META["REMOTE_ADDR"],
        "login_url_": login_url,
        "logout_url_": logout_url,
        "is_webmaster_": users.is_webmaster(user),
    }


def powered_by_processor(request):
    return {
        "website_version_": website_version(),
        "python_version_": python_version(),
        "django_version_": django_version(),
    }



# EOF
