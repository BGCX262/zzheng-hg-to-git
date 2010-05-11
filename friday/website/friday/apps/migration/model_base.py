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

from django.conf import settings
from google.appengine.ext import db


class MigrationModel(db.Expando):

    to_schema_version = None

    schema_version = db.IntegerProperty(required=True)

    def pk(self):
        if self.is_saved():
            return self.key().id() or self.key().name()
        else:
            raise AttributeError("%s object has no attribute 'pk'" % self.__class__.__name__)

    def save(self):
        super(MigrationModel, self).put()

    def upgrade(self):
        raise NotImplementedError("sub-class should implement upgrade()")

    @classmethod
    def find_old(cls, limit):
        gql = "WHERE schema_version = :schema_version ORDER BY __key__ LIMIT %d" % limit
        schema_version = cls.to_schema_version - 1
        old_instances = cls.gql(gql, schema_version=schema_version)
        return old_instances

    @classmethod
    def has_old(cls):
        gql = "WHERE schema_version < :to_schema_version LIMIT 1"
        old_instances = cls.gql(gql, to_schema_version=cls.to_schema_version)
        return old_instances.count() > 0

    @classmethod
    def migrate(cls, limit=None):
        succeeded, failed = 0, 0
        limit = limit or getattr(settings, "MY_MIGRATION_NUM_PER_REQUEST", 20)
        old_instances = cls.find_old(limit)
        for instance in old_instances:
            try:
                instance.upgrade()
                instance.schema_version = cls.to_schema_version
                instance.save()
                succeeded += 1
            except Exception, exc:
                logging.error("Failed to migrate %s %s: %s" % (cls.__name__, instance.pk, exc))
                logging.exception(exc)
                failed += 1
        return succeeded, failed


# EOF
