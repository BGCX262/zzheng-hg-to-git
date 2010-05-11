#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-03.
# $Id$
#

import datetime
import logging

from google.appengine.ext import db

from friday.apps.migration.model_base import MigrationModel


class _Model_v1(MigrationModel):

    to_schema_version = 1

    def upgrade(self):
        pass


# --------------------------------------------------------------------------------------------------


class Activity(_Model_v1): pass

class Attender(_Model_v1): pass

class Comment(_Model_v1): pass

class Group(_Model_v1): pass

class Member(_Model_v1): pass

class Notification(_Model_v1): pass

class Profile(_Model_v1): pass

class Resto(_Model_v1): pass

class Tag(_Model_v1): pass


def get_to_schema_version():
    return _Model_v1.to_schema_version


# EOF
