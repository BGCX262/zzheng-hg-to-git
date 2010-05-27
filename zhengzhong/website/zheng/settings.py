#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-05.
# $Id$
#

import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ("ZHENG Zhong", "@".join(["heavyzheng", "gmail.com"])),
)

MANAGERS = ADMINS

# Database configurations.
# @appengine: Django models are not supported: set all DATABASE_* to empty.
DATABASE_ENGINE = ""
DATABASE_NAME = ""
DATABASE_USER = ""
DATABASE_PASSWORD = ""
DATABASE_HOST = ""
DATABASE_PORT = ""

# Local time zone for this installation. Choices can be found here:
#   http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "UTC"

# Language code for this installation. All choices can be found here:
#   http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
#   http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = "en-us"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ""

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ""

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = "/media/"

# Make this unique, and don't share it with anybody.
SECRET_KEY = "*c(^-34)gdt8=g%3##=*apdl$!w8q-$4bc96+25!%2@%6-pj*x"

# List of callables that automatically populates the context with a few variables.
TEMPLATE_CONTEXT_PROCESSORS = (
    "zheng.common.context_processors.common_data_processor",
    "zheng.common.context_processors.current_user_processor",
    "zheng.common.context_processors.powered_by_processor",
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.load_template_source",
    "django.template.loaders.app_directories.load_template_source",
    #"django.template.loaders.eggs.load_template_source",
)

TEMPLATE_DIRS = (os.path.normpath(os.path.join(os.path.dirname(__file__), "templates")),)

TEMPLATE_STRING_IF_INVALID = "#TEMPLATE_ERROR#"

MIDDLEWARE_CLASSES = (
    "django.middleware.common.CommonMiddleware",
    #"django.contrib.sessions.middleware.SessionMiddleware",  # @appengine: comment this line!
    #"django.middleware.locale.LocaleMiddleware",
    #"django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.doc.XViewMiddleware",

    "zheng.common.middlewares.RenderErrorMiddleware",
)

ROOT_URLCONF = "zheng.urls"

# For serving static files.
STATIC_DOC_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "static"))

INSTALLED_APPS = (
    #"django.contrib.admin",
    #"django.contrib.auth",
    #"django.contrib.contenttypes",
    #"django.contrib.sessions",
    #"django.contrib.sites",
    #"django.contrib.webdesign",

    "zheng",  # for loading templates
    "zheng.apps.homepage",
)


#---------------------------------------------------------------------------------------------------

# All the MY_* settings are website-specific.

MY_STATIC_URL_PREFIX = "/static"
MY_ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))

MY_EMAIL_DOMAIN = "gmail.com"
MY_WEBMASTER_EMAILS = (
    "@".join(["heavyzheng", MY_EMAIL_DOMAIN]),
)


# EOF
