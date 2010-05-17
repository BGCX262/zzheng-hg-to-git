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
from djangomockup.models.signals import pre_delete
from friday.auth import users
from friday.common.dbutils import filter_key, ord_to_key
from friday.apps.tagging.models import Taggable
from friday.apps.ilike.models import Fan


_RESTO_CATEGORIES = (
    ("chinese", "Chinese Food"),
    ("japanese", "Japanese Food"),
    ("korean", "Korean Food"),
    ("southeast_asian", "Southeast Asian Food"),
    ("french", "French Food"),
    ("italian", "Italian Food"),
    ("misc", "Misc."),
)


_DEFAULT_RESTO_CATEGORY = "misc"


class Resto(models.Model, Taggable):

    CATEGORIES = _RESTO_CATEGORIES
    DEFAULT_CATEGORY = _DEFAULT_RESTO_CATEGORY

    tags_attr = "tags"  # Required by Taggable mixin class.

    name = db.StringProperty(required=True)
    description = db.TextProperty()

    category = db.StringProperty(
        required=True,
        choices=[category for category, display in _RESTO_CATEGORIES],
        default=_DEFAULT_RESTO_CATEGORY
    )

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

    popularity = db.IntegerProperty(required=True, default=0)

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

    def get_category_display(self):
        for category, display in self.CATEGORIES:
            if category == self.category:
                return display
        return self.category

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
    def find(cls, **kwargs):
        query = cls.objects.order_by(kwargs.get("order_by") or "-popularity")
        if kwargs.get("cursor"):
            query.with_cursor(kwargs["cursor"])
        if kwargs.get("limit"):
            query.set_limit(kwargs["limit"])
        return query

    @classmethod
    def find_by_category(cls, category, **kwargs):
        query = cls.objects.filter(category=category)
        query = query.order_by(kwargs.get("order_by") or "-popularity")
        if kwargs.get("cursor"):
            query.with_cursor(kwargs["cursor"])
        if kwargs.get("limit"):
            query.set_limit(kwargs["limit"])
        return query

    @classmethod
    def find_by_tag(cls, name, **kwargs):
        if "order_by" not in kwargs:
            kwargs["order_by"] = "-popularity"
        return super(Resto, cls).find_by_tag(name=name, **kwargs)


class Dish(models.Model):

    resto = db.ReferenceProperty(Resto, required=True)
    name = db.StringProperty(required=True)
    description = db.TextProperty()
    photo_url = db.LinkProperty()
    is_spicy = db.BooleanProperty(required=True, default=False)
    is_vegetarian = db.BooleanProperty(required=True, default=False)
    price = db.StringProperty()
    popularity = db.IntegerProperty(required=True, default=0)

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
            self.popularity += 1
        else:
            fan.delete()
            self.popularity = max(0, self.popularity - 1)
        self.save()

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
        query = cls.objects.filter(resto=resto).order_by("-popularity")
        return query

    @classmethod
    def find_by_name(cls, name):
        query = cls.objects.filter(name=name).order_by("-popularity")
        return query

    @classmethod
    def delete_related(cls, resto):
        deleted = 0
        query = cls.objects.filter(resto=resto)
        for instance in query:
            instance.delete()
            deleted += 1
        return deleted


#---------------------------------------------------------------------------------------------------


def delete_related_dishes(sender, **kwargs):
    if sender == Resto:
        try:
            resto = kwargs["instance"]
            deleted = Dish.delete_related(resto=resto)
            if deleted > 0:
                logging.info("%s related dishes have been deleted successfully." % deleted)
        except Exception, exc:
            logging.error("Failed to delete related dishes on resto: %s" % exc)
            logging.exception(exc)


pre_delete.connect(delete_related_dishes, sender=Resto)


# EOF
