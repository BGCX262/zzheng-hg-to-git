#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-19.
# $Id$
#

import datetime
import logging

from google.appengine.ext import db

from djangomockup import models
from friday.auth import users
from friday.common.dbutils import filter_key, ord_to_key
from friday.apps.poststats.signals import post_received


class GroupPostStat(models.Model):

    google_group = db.StringProperty(required=True)
    start_date = db.DateProperty(required=True)
    post_count = db.IntegerProperty(required=True, default=0)

    def top_posters(self, limit=None):
        limit = limit or 3
        query = MemberPostStat.objects.filter(group_post_stat=self).order_by("-post_count")
        query.set_limit(limit)
        return query

    @classmethod
    def _make_pk(cls, google_group, date):
        return "%s/%s/%s" % (filter_key(google_group), date.year, date.month)

    @classmethod
    def get_or_create(cls, google_group):
        today = datetime.date.today()
        pk = cls._make_pk(google_group, today)
        try:
            instance = cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            instance = cls(key_name=pk, google_group=google_group, start_date=today)
            instance.save()
        return instance

    @classmethod
    def get_unique(cls, google_group, date):
        pk = cls._make_pk(google_group, date)
        try:
            instance = cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            instance = None
        return instance


class MemberPostStat(models.Model):

    group_post_stat = db.ReferenceProperty(GroupPostStat, required=True)
    poster = db.ReferenceProperty(users.User, required=True)
    post_count = db.IntegerProperty(required=True, default=0)

    def __unicode__(self):
        return unicode(self.poster)

    @classmethod
    def _make_pk(cls, group_post_stat, poster):
        return "%s/%s" % (group_post_stat.pk, poster.email)

    @classmethod
    def get_or_create(cls, group_post_stat, poster):
        pk = cls._make_pk(group_post_stat, poster)
        try:
            instance = cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            instance = cls(key_name=pk, group_post_stat=group_post_stat, poster=poster)
            instance.save()
        return instance

    @classmethod
    def get_unique(cls, group_post_stat, poster):
        pk = cls._make_pk(group_post_stat, poster)
        try:
            instance = cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            instance = None
        return instance


#---------------------------------------------------------------------------------------------------


def count_post(sender, **kwargs):
    try:
        poster = users.get_user(kwargs["poster"])
        recipients = kwargs["recipients"]
        google_groups = [
            recipient.split("@", 1)[0]
            for recipient in recipients
            if recipient.endswith("@googlegroups.com")
        ]
        google_groups = set(google_groups)  # to remove duplicates.
        for google_group in google_groups:
            # TODO: currently we support only vivelevendredi Google Group.
            if google_group != "vivelevendredi":
                continue
            group_post_stat = GroupPostStat.get_or_create(google_group=google_group)
            group_post_stat.post_count += 1
            group_post_stat.save()
            member_post_stat = MemberPostStat.get_or_create(
                group_post_stat=group_post_stat,
                poster=poster
            )
            member_post_stat.post_count += 1
            member_post_stat.save()
    except Exception, exc:
        logging.error("Failed to count post: %s" % exc)
        logging.exception(exc)


post_received.connect(count_post)


# EOF
