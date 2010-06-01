#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-11.
# $Id$
#

import logging

from google.appengine.ext import db

from djangomockup import models
from djangomockup.models.signals import pre_delete
from friday.auth import users


class Fan(models.Model):

    MIN_RATING = 1
    MAX_RATING = 5

    ref_type = db.StringProperty(required=True)
    ref_pk = db.StringProperty(required=True)
    user = db.ReferenceProperty(users.User, required=True)
    rating = db.IntegerProperty(required=True)
    rate_date = db.DateTimeProperty(auto_now_add=True)

    schema_version = db.IntegerProperty(required=True, default=1)

    @classmethod
    def _make_pk(cls, ref_type, ref_pk, user):
        # Note: we do not filter ref_type and ref_pk.
        # - ref_type is a class name so upper-cased letters are allowed.
        # - ref_pk is already a valid key.
        return "%s/%s/%s" % (ref_type, ref_pk, user.email.lower())

    @classmethod
    def create(cls, ref_type, ref_pk, user, rating):
        pk = cls._make_pk(ref_type, ref_pk, user)
        rating = max(cls.MIN_RATING, min(cls.MAX_RATING, rating))
        return cls(
            key_name=pk,
            ref_type=ref_type,
            ref_pk=str(ref_pk),
            user=user,
            rating=rating
        )

    @classmethod
    def create_fan(cls, ref_type, ref_pk, user):
        pk = cls._make_pk(ref_type, ref_pk, user)
        return cls(
            key_name=pk,
            ref_type=ref_type,
            ref_pk=str(ref_pk),
            user=user,
            rating=cls.MAX_RATING
        )

    @classmethod
    def get_unique(cls, ref_type, ref_pk, user):
        pk = cls._make_pk(ref_type, ref_pk, user)
        try:
            instance = cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            instance = None
        return instance

    @classmethod
    def find(cls, ref_type, ref_pk, **kwargs):
        query = cls.objects.filter(ref_type=ref_type, ref_pk=str(ref_pk)).order_by("-rate_date")
        if kwargs.get("limit"):
            query.set_limit(kwargs["limit"])
        return query

    @classmethod
    def find_fans(cls, ref_type, ref_pk):
        query = cls.objects.filter(ref_type=ref_type, ref_pk=str(ref_pk), rating=cls.MAX_RATING)
        return query

    @classmethod
    def delete_related(cls, ref_type, ref_pk):
        deleted = 0
        query = cls.objects.filter(ref_type=ref_type, ref_pk=str(ref_pk))
        for instance in query:
            instance.delete()
            deleted += 1
        return deleted


class Fave(models.Model):

    ref_type = db.StringProperty(required=True)
    ref_pk = db.StringProperty(required=True)
    user = db.ReferenceProperty(users.User, required=True)
    add_date = db.DateTimeProperty(auto_now_add=True)

    schema_version = db.IntegerProperty(required=True, default=1)

    @classmethod
    def _make_pk(cls, ref_type, ref_pk, user):
        # Note: we do not filter ref_type and ref_pk.
        # - ref_type is a class name so upper-cased letters are allowed.
        # - ref_pk is already a valid key.
        return "%s/%s/%s" % (ref_type, ref_pk, user.email.lower())

    @classmethod
    def create(cls, ref_type, ref_pk, user):
        pk = cls._make_pk(ref_type, ref_pk, user)
        return cls(key_name=pk, ref_type=ref_type, ref_pk=str(ref_pk), user=user)

    @classmethod
    def get_unique(cls, ref_type, ref_pk, user):
        pk = cls._make_pk(ref_type, ref_pk, user)
        try:
            instance = cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            instance = None
        return instance

    @classmethod
    def find_by_user(cls, ref_type, user, **kwargs):
        query = cls.objects.filter(ref_type=ref_type, user=user).order_by("-add_date")
        if kwargs.get("limit"):
            query.set_limit(kwargs["limit"])
        return query

    @classmethod
    def find_by_ref(cls, ref_type, ref_pk, **kwargs):
        query = cls.objects.filter(ref_type=ref_type, ref_pk=str(ref_pk)).order_by("-add_date")
        if kwargs.get("limit"):
            query.set_limit(kwargs["limit"])
        return query

    @classmethod
    def delete_related(cls, ref_type, ref_pk):
        deleted = 0
        query = cls.objects.filter(ref_type=ref_type, ref_pk=str(ref_pk))
        for instance in query:
            instance.delete()
            deleted += 1
        return deleted


#---------------------------------------------------------------------------------------------------


def delete_related_fans(sender, **kwargs):
    if sender != Fan:
        try:
            instance = kwargs["instance"]
            deleted = Fan.delete_related(ref_type=sender.__name__, ref_pk=instance.pk)
            if deleted > 0:
                logging.info("%s related fans have been deleted successfully." % deleted)
        except Exception, exc:
            logging.error("Failed to delete related fans of instance: %s" % exc)
            logging.exception(exc)


def delete_related_faves(sender, **kwargs):
    if sender != Fave:
        try:
            instance = kwargs["instance"]
            deleted = Fave.delete_related(ref_type=sender.__name__, ref_pk=instance.pk)
            if deleted > 0:
                logging.info("%s related faves have been deleted successfully." % deleted)
        except Exception, exc:
            logging.error("Failed to delete related faves of instance: %s" % exc)
            logging.exception(exc)


pre_delete.connect(delete_related_fans)
pre_delete.connect(delete_related_faves)


# EOF
