#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-04-14.
# $Id$
#

import re


__all__ = ("Browser",)


_BROWSERS = (

    # Opera likes to pretend to be some other browser, so detect it first.
    (re.compile(r"(?P<id>Opera)[/\s](?P<version>[\w\.\-]+)"), "Opera"),

    (re.compile(r"(?P<id>MSIE)\s(?P<version>[\w\.\-]+)"), "Microsoft Internet Explorer"),
    (re.compile(r"(?P<id>Firefox)/(?P<version>[\w\.\-]+)"), "Mozilla Firefox"),
    (re.compile(r"(?P<id>Chrome)/(?P<version>[\w\.\-]+)"), "Google Chrome"),
    (re.compile(r"(?P<id>Safari)/(?P<version>[\w\.\-]+)"), "Safari"),
)


def _parse_browser(user_agent):
    user_agent = user_agent or ""
    for expr, browser_name in _BROWSERS:
        match = expr.search(user_agent)
        if match:
            return (match.group("id"), browser_name, match.group("version"))
    return (None, None, None)


def _parse_platform(user_agent):
    user_agent = user_agent or ""
    expr = re.compile(r"(?P<platform>Windows|Linux|Mac\sOS\sX|FreeBSD|OpenBSD)")
    match = expr.search(user_agent)
    if match:
        return match.group("platform")
    else:
        return None


class Browser(object):

    def __init__(self, user_agent):
        self.user_agent = user_agent or None
        self.id, self.name, self.version = _parse_browser(user_agent)
        self.platform = _parse_platform(user_agent)

    def __str__(self):
        return "%s %s (%s)" % (self.name, self.version, self.platform)

    def __unicode__(self):
        return u"%s %s (%s)" % (self.name, self.version, self.platform)


# EOF
