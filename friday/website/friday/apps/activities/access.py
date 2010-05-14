#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

from friday.auth import users
from friday.apps.groups.access import GroupAccess
from friday.apps.activities.models import Activity, Attender


class ActivityAccess(object):

    def __init__(self, activity, user):
        self._activity = activity
        self._user = user
        self._group_access = GroupAccess(activity.group, user)

    @property
    def group_access(self):
        return self._group_access

    def can_edit(self):
        if not self._user:
            return False
        if users.is_webmaster(self._user):
            return True
        return (self._activity.submitter == self._user)

    def can_delete(self):
        if not self._user:
            return False
        if users.is_webmaster(self._user):
            return True
        return (self._activity.submitter == self._user)

    def can_attend(self):
        if self._activity.is_past or self._activity.is_closed:
            return False
        if not self._user:
            return False
        if self._activity.places and self._activity.headcount >= self._activity.places:
            return False
        attender = Attender.get_unique(activity=self._activity, user=self._user)
        return attender is None

    def can_quit(self):
        if self._activity.is_past:
            return False
        if not self._user:
            return False
        attender = Attender.get_unique(activity=self._activity, user=self._user)
        return attender is not None



# EOF
