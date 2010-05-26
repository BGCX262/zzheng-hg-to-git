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
from friday.common.dbutils import filter_key
from friday.apps.groups.models import Group


class GroupStat(models.Model):

    group = db.ReferenceProperty(Group, required=True)
    start_date = db.DateProperty(required=True)
    post_count = db.IntegerProperty(required=True, default=0)

    @property
    def top_posters(self):
        return PosterStat.find_by_group_stat(group_stat=self, limit=3)

    @classmethod
    def _make_pk(cls, group, date):
        return "%s/%s/%s" % (group.uid, date.year, date.month)

    @classmethod
    def get_unique(cls, group, date, month_delta=None):
        if month_delta:
            month_count = date.year * 12 + date.month + month_delta
            year = month_count // 12
            month = month_count % 12
            if month == 0:
                year -= 1
                month = 12
            date = datetime.date(year, month, 1)
        pk = cls._make_pk(group, date)
        try:
            instance = cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            instance = None
        return instance

    @classmethod
    def get_or_create(cls, group, date):
        instance = cls.get_unique(group=group, date=date)
        if instance is None:
            pk = cls._make_pk(group, date)
            instance = cls(key_name=pk, group=group, start_date=date)
            instance.save()
        return instance


class PosterStat(models.Model):

    group_stat = db.ReferenceProperty(GroupStat, required=True)
    poster = db.ReferenceProperty(users.User, required=True)
    post_count = db.IntegerProperty(required=True, default=0)

    def __unicode__(self):
        return unicode(self.poster)

    @classmethod
    def _make_pk(cls, group_stat, poster):
        return "%s/%s" % (group_stat.pk, poster.email.lower())

    @classmethod
    def get_unique(cls, group_stat, poster):
        pk = cls._make_pk(group_stat, poster)
        try:
            instance = cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            instance = None
        return instance

    @classmethod
    def get_or_create(cls, group_stat, poster):
        instance = cls.get_unique(group_stat=group_stat, poster=poster)
        if instance is None:
            pk = cls._make_pk(group_stat, poster)
            instance = cls(key_name=pk, group_stat=group_stat, poster=poster)
            instance.save()
        return instance

    @classmethod
    def find_by_group_stat(cls, group_stat, **kwargs):
        query = cls.objects.filter(group_stat=group_stat).order_by("-post_count")
        if kwargs.get("limit"):
            query.set_limit(kwargs["limit"])
        return query


#---------------------------------------------------------------------------------------------------


def count_post(subject, poster_email, recipients):
    # TODO: currently we support only vivelevendredi Google Group.
    RECIPIENT_TO_GROUP_UID = {
        "vivelevendredi@googlegroups.com": "vivelevendredi",
    }
    try:
        recipients = [
            recipient.lower()
            for recipient in recipients
            if recipient.lower() in RECIPIENT_TO_GROUP_UID
        ]
        recipients = set(recipients)  # to remove duplicates.
        for recipient in recipients:
            group = Group.get_unique(uid=RECIPIENT_TO_GROUP_UID[recipient])
            if group is None:
                logging.warning("Ignored recipient %s: group cannot be found." % recipient)
                continue
            group_stat = GroupStat.get_or_create(group=group, date=datetime.date.today())
            group_stat.post_count += 1
            group_stat.save()
            poster = users.get_user_by_email(poster_email)
            if poster is None:
                logging.warning("Ignored poster %s: user cannot be found." % poster_email)
            else:
                poster_stat = PosterStat.get_or_create(group_stat=group_stat, poster=poster)
                poster_stat.post_count += 1
                poster_stat.save()
    except Exception, exc:
        logging.error("Failed to count post: %s" % exc)
        logging.exception(exc)


# EOF
