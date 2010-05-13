#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-18.
# $Id$
#

from friday.auth import users
from friday.apps.restos.models import Resto


class RestoAccess(object):

    def __init__(self, user, resto):
        self._user = user
        self._resto = resto

    def can_edit(self):
        if users.is_webmaster(self._user):
            return True
        elif self._user and self._resto.owner:
            return self._user == self._resto.owner
        else:
            return False

    def can_delete(self):
        if users.is_webmaster(self._user):
            return True
        elif self._user and self._resto.owner:
            return self._user == self._resto.owner
        else:
            return False


# EOF
