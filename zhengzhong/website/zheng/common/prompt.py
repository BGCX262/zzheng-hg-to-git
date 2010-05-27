#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

import urllib
from django.http import HttpRequest


class Prompt(object):

    INFO = "info"
    ERROR = "error"

    def __init__(self, **kwargs):
        self.severity = None
        self.message = None
        if kwargs.get("request"):
            request_dict = kwargs["request"].REQUEST
        else:
            request_dict = kwargs
        if request_dict.get(Prompt.ERROR):
            self.severity = Prompt.ERROR
            self.message = request_dict[Prompt.ERROR]
        elif request_dict.get(Prompt.INFO):
            self.severity = Prompt.INFO
            self.message = request_dict[Prompt.INFO]

    def __nonzero__(self):
        return bool(self.message)

    def __str__(self):
        return str(self.message)

    def __unicode__(self):
        return unicode(self.message)

    @property
    def id(self):
        return "prompt-%s-%d" % (self.severity, abs(hash(self.message)))

    def as_dict(self):
        if self.severity and self.message:
            return {self.severity: self.message}
        else:
            return {}

    def urlencode(self):
        return urllib.urlencode(self.as_dict())


# EOF

