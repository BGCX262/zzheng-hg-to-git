#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

import datetime
import logging

from google.appengine.ext import db

from djangomockup import models
from djangomockup.models.signals import pre_delete
from friday.auth import users
from friday.apps.groups.models import Group


class Activity(models.Model):

    group = db.ReferenceProperty(Group, required=True)
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    date = db.DateProperty(required=True)
    address = db.PostalAddressProperty()
    city = db.StringProperty(required=True)
    geo_pt = db.GeoPtProperty()
    places = db.IntegerProperty()
    related_link = db.LinkProperty()
    is_closed = db.BooleanProperty(required=True, default=False)
    submitter = db.ReferenceProperty(users.User, required=True)
    submit_date = db.DateProperty(auto_now_add=True)

    schema_version = db.IntegerProperty(required=True, default=1)

    @property
    def model_name(self):
        return self.__class__.__name__

    @property
    def is_past(self):
        return self.date < datetime.date.today()

    @property
    def attenders(self):
        return Attender.find_by_activity(self)

    @property
    def headcount(self):
        headcount = 0
        for attender in self.attenders:
            headcount += 1 + attender.with_friends
        return headcount

    def __unicode__(self):
        return unicode(self.title)

    @classmethod
    def get_unique(cls, id, group):
        try:
            instance = cls.objects.get(id=id)
        except cls.DoesNotExist:
            instance = None
        if instance is not None and instance.group.uid != group.uid:
            instance = None
        return instance

    @classmethod
    def create(cls, group, **kwargs):
        return cls(group=group, **kwargs)

    @classmethod
    def find_all(cls, group, **kwargs):
        query = cls.objects.filter(group=group).order_by("-date")
        if kwargs.get("limit"):
            query.set_limit(kwargs["limit"])
        return query

    @classmethod
    def find_upcoming(cls, group, **kwargs):
        today = datetime.date.today()
        query = cls.objects.filter(group=group, date__gte=today).order_by("-date")
        if kwargs.get("limit"):
            query.set_limit(kwargs["limit"])
        return query


class Attender(models.Model):

    activity = db.ReferenceProperty(Activity, required=False)
    user = db.ReferenceProperty(users.User, required=True)
    with_friends = db.IntegerProperty(required=True, default=0)

    schema_version = db.IntegerProperty(required=True, default=1)

    def __unicode__(self):
        return unicode(self.user)

    @property
    def username(self):
        return self.user.username

    @classmethod
    def _make_pk(cls, activity, user):
        return "%s/%s" % (activity.id, user.email.lower())

    @classmethod
    def create(cls, activity, user, **kwargs):
        pk = cls._make_pk(activity, user)
        if "with_friends" in kwargs and kwargs["with_friends"] is None:
            del kwargs["with_friends"]
        return cls(key_name=pk, activity=activity, user=user, **kwargs)

    @classmethod
    def get_unique(cls, activity, user):
        pk = cls._make_pk(activity, user)
        try:
            instance = cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            instance = None
        return instance

    @classmethod
    def find_by_activity(cls, activity, **kwargs):
        query = cls.objects.filter(activity=activity).order_by(kwargs.get("order_by") or "user")
        return query

    @classmethod
    def delete_related(cls, activity):
        deleted = 0
        query = cls.objects.filter(activity=activity)
        for instance in query:
            instance.delete()
            deleted += 1
        return deleted


#---------------------------------------------------------------------------------------------------


def delete_related_attenders(sender, **kwargs):
    if sender == Activity:
        try:
            activity = kwargs["instance"]
            deleted = Attender.delete_related(activity=activity)
            if deleted > 0:
                logging.info("%s related attenders have been deleted successfully." % deleted)
        except Exception, exc:
            logging.error("Failed to delete related attenders of activity: %s" % exc)
            logging.exception(exc)


pre_delete.connect(delete_related_attenders, sender=Activity)


# EOF
