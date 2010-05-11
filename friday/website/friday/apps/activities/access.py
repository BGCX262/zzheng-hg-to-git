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
        elif users.is_webmaster(self._user):
            return True
        else:
            return (self._activity.submitter == self._user)

    def can_delete(self):
        if not self._user:
            return False
        elif users.is_webmaster(self._user):
            return True
        else:
            return (self._activity.submitter == self._user)

    def can_join(self):
        if not self._user:
            return False
        else:
            attender = Attender.get_unique(activity=self._activity, user=self._user)
            return attender is None

    def can_quit(self):
        if not self._user:
            return False
        else:
            attender = Attender.get_unique(activity=self._activity, user=self._user)
            return attender is not None



# EOF
