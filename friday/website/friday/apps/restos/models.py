#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-18.
# $Id$
#

import logging

from google.appengine.ext import db

from djangomockup import models
from friday.auth import users
from friday.common.dbutils import filter_key, ord_to_key
from friday.apps.tagging.models import Taggable
from friday.apps.ilike.models import Fan


class Resto(models.Model, Taggable):

    tags_attr = "tags"  # Required by Taggable mixin class.

    name = db.StringProperty(required=True)
    description = db.TextProperty()

    address = db.PostalAddressProperty(required=True)
    city = db.StringProperty(required=True)
    geo_pt = db.GeoPtProperty()
    post_code = db.StringProperty()
    route = db.StringProperty()

    tel_1 = db.PhoneNumberProperty()
    tel_2 = db.PhoneNumberProperty()
    website = db.LinkProperty()

    hours_1 = db.StringProperty()
    hours_2 = db.StringProperty()
    hours_3 = db.StringProperty()
    places = db.IntegerProperty()

    tags = db.StringListProperty(default=[])

    background_url = db.LinkProperty()
    logo_icon_url = db.LinkProperty()

    owner = db.ReferenceProperty(users.User, required=False, collection_name="owned_restos")
    submitter = db.ReferenceProperty(users.User, required=True, collection_name="submitted_restos")
    submit_date = db.DateTimeProperty(required=True, auto_now_add=True)
    updater = db.ReferenceProperty(users.User, required=True, collection_name="updated_restos")
    update_date = db.DateTimeProperty(required=True, auto_now=True)

    schema_version = db.IntegerProperty(required=True, default=1)

    @property
    def model_name(self):
        return self.__class__.__name__

    @property
    def tels(self):
        tel_list = []
        if self.tel_1:
            tel_list.append(self.tel_1)
        if self.tel_2:
            tel_list.append(self.tel_2)
        return tel_list

    @property
    def hours(self):
        hours_list = []
        if self.hours_1:
            hours_list.append(self.hours_1)
        if self.hours_2:
            hours_list.append(self.hours_2)
        if self.hours_3:
            hours_list.append(self.hours_3)
        return hours_list

    @property
    def dishes(self):
        return Dish.find_by_resto(resto=self)

    def __unicode__(self):
        return unicode(self.name)

    def delete(self):
        if self.tags:
            self.remove_tags(",".join(self.tags))
        return super(Resto, self).delete()

    @classmethod
    def get_unique(cls, id):
        try:
            instance = cls.objects.get(id=id)
        except cls.DoesNotExist:
            instance = None
        return instance

    @classmethod
    def create(cls, submitter, **kwargs):
        return cls(submitter=submitter, updater=submitter, **kwargs)

    @classmethod
    def find_all(cls, **kwargs):
        query = cls.objects.order_by(kwargs.get("order_by") or "-update_date")
        if kwargs.get("limit"):
            query = query[:kwargs["limit"]]
        return query


class Dish(models.Model):

    resto = db.ReferenceProperty(Resto, required=True)
    name = db.StringProperty(required=True)
    description = db.TextProperty()
    photo_url = db.LinkProperty()
    is_spicy = db.BooleanProperty(required=True, default=False)
    is_vegetarian = db.BooleanProperty(required=True, default=False)
    price = db.StringProperty()

    schema_version = db.IntegerProperty(required=True, default=1)

    @property
    def fans(self):
        return Fan.find_fans(ref_type=self.__class__.__name__, ref_pk=self.id)

    def __unicode__(self):
        return unicode(self.name)

    def like_or_unlike(self, user):
        fan = Fan.get_unique(ref_type=self.__class__.__name__, ref_pk=self.id, user=user)
        if not fan:
            fan = Fan.create_fan(ref_type=self.__class__.__name__, ref_pk=self.id, user=user)
            fan.save()
        else:
            fan.delete()

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)

    @classmethod
    def get_unique(cls, id):
        try:
            instance = cls.objects.get(id=id)
        except cls.DoesNotExist:
            instance = None
        return instance

    @classmethod
    def find_by_resto(cls, resto):
        query = cls.objects.filter(resto=resto)
        return query


# EOF
