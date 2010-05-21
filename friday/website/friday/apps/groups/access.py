#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

from friday.auth import users
from friday.apps.groups.models import Group, Member


class GroupAccess(object):

    def __init__(self, group, user):
        self._group = group
        self._user = user
        if user:
            self._member = Member.get_unique(group=group, user=user)
        else:
            self._member = None

    @property
    def member(self):
        return self._member

    def can_administrate(self):
        if users.is_webmaster(self._user):
            return True
        if self._user and self._user == self._group.owner:
            return True
        if self._member and self._member.is_approved:
            return self._member.role == Member.ADMINISTRATOR
        return False

    def can_moderate(self):
        if self.can_administrate():
            return True
        if self._member and self._member.is_approved:
            return self._member.role == Member.MODERATOR
        return False

    def can_contribute(self):
        if self.can_moderate():
            return True
        return self._member and self._member.is_approved

    def can_join(self):
        return self._user and self._member is None

    def can_quit(self):
        return self._user and self._member is not None



# EOF
