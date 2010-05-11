#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-04-27.
# $Id$
#

import random

from google.appengine.ext import db

from djangomockup import models
from friday.common.dbutils import filter_key, ord_to_key


class TagCloud(object):

    class _Tag(object):

        def __init__(self, tag, average_count):
            super(TagCloud._Tag, self).__init__()
            self._tag = tag
            self._average_count = average_count

        def __unicode__(self):
            return unicode(self._tag)

        def __str__(self):
            return str(self._tag)

        def category(self):
            return self._tag.category

        def name(self):
            return self._tag.name

        def count(self):
            return self._tag.count

        def size(self):
            size = int(100 * self._tag.count / self._average_count)
            return max(90, min(size, 120))

    def __init__(self, tags):
        super(TagCloud, self).__init__()
        total_count = 0
        total_tags = 0
        for tag in tags:
            total_count += tag.count
            total_tags += 1
        if total_count > 0 and total_tags > 0:
            average_count = float(total_count) / total_tags
            self.tags = [TagCloud._Tag(tag, average_count) for tag in tags]
            random.shuffle(self.tags)
        else:
            self.tags = []

    def __nonzero__(self):
        return bool(self.tags)


class Tag(models.Model):

    category = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    count = db.IntegerProperty(required=True, default=0)
    schema_version = db.IntegerProperty(required=True, default=1)

    def __unicode__(self):
        return unicode(self.name)

    @classmethod
    def _make_pk(cls, category, name):
        return "%s/%s" % (filter_key(category), ord_to_key(name))

    @classmethod
    def get_unique(cls, category, name):
        pk = cls._make_pk(category, name)
        try:
            instance = cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            instance = None
        return instance

    @classmethod
    def get_or_create(cls, category, name):
        instance = cls.get_unique(category=category, name=name)
        if instance is None:
            pk = cls._make_pk(category, name)
            instance = cls(key_name=pk, category=category, name=name)
            return instance, True
        else:
            return instance, False

    @classmethod
    def find(cls, category=None, **kwargs):
        query = cls.objects.all()
        if isinstance(category, type):
            category = category.__name__
        if category:
            query = query.filter(category=category)
        query = query.order_by(kwargs.get("order_by") or "-count")
        if kwargs.get("limit"):
            query = query[:kwargs["limit"]]
        return query

    @classmethod
    def get_cloud(cls, category, limit=None):
        tags = cls.find(category=category, limit=limit)
        return TagCloud(tags)


class Taggable(object):
    """
    Taggable mixin class. Requirements for sub-classes are:
    - must have a class attribute 'tags_attr', which is the attribute name of tags.
    - self.save(): saves the instance to database.
    """

    tag_category = None
    tags_attr = None
    force_lower_case = True

    def __get_tag_category(self):
        return self.__class__.tag_category or self.__class__.__name__

    def add_tags(self, names):
        existing_tags = getattr(self, self.__class__.tags_attr, [])
        if self.force_lower_case:
            names = names.lower()
        name_list = names.replace(",", " ").replace(";", " ").split()
        for name in name_list:
            # Get or create the tag by name.
            tag, created = Tag.get_or_create(self.__get_tag_category(), name)
            if created:
                tag.save()
            # Process the tag name on the instance.
            if name not in existing_tags:
                # Increase the tag counter and save.
                tag.count += 1
                tag.save()
                # Update existing tags on the instance.
                existing_tags.append(name)
        # Update tags on the instance (do NOT save).
        setattr(self, self.__class__.tags_attr, existing_tags)

    def remove_tags(self, names):
        existing_tags = getattr(self, self.__class__.tags_attr, [])
        if self.force_lower_case:
            names = names.lower()
        name_list = names.replace(",", " ").replace(";", " ").split()
        for name in name_list:
            if name in existing_tags:
                # Update existing tags on the instance.
                while name in existing_tags:
                    existing_tags.remove(name)
                # Decrease the tag counter and save (or delete), as necessary.
                tag = Tag.get_unique(category=self.__get_tag_category(), name=name)
                if tag:
                    tag.count -= 1
                    if tag.count > 0:
                        tag.save()
                    else:
                        tag.delete()
        # Update tags on the instance (do NOT save).
        setattr(self, self.__class__.tags_attr, existing_tags)

    @classmethod
    def find_by_tag(cls, name, **kwargs):
        filter_kwargs = {cls.tags_attr: name}
        query = cls.objects.filter(**filter_kwargs)
        if "order_by" in kwargs:
            query = query.order_by(kwargs["order_by"])
        if kwargs.get("limit"):
            query = query[:kwargs["limit"]]
        return query


# EOF
