#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2009-10-29.
# $Id$
#


__all__ = ("Error", "ProgrammingError", "BadRequestError", "InvalidFormError",)


class Error(Exception): pass


class ProgrammingError(Error): pass


class EntityNotFoundError(Error):
    def __init__(self, model_class, searched_by):
        message = u"%s not found: %s" % (model_class.__name__, searched_by)
        super(EntityNotFoundError, self).__init__(message)


class InvalidFormError(Error):
    def __init__(self, errors):
        bad_fields = u", ".join(errors.keys())
        message = u"Invalid value(s) in field(s): %s." % bad_fields
        super(InvalidFormError, self).__init__(message)


class BadRequestError(Error):

    def __init__(self, request, message):
        super(BadRequestError, self).__init__(message)
        self._path = request.path
        self._method = request.method

    @property
    def path(self):
        return self._path

    @property
    def method(self):
        return self._method


# EOF
