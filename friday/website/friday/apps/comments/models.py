#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-15.
# $Id$
#

import logging

from google.appengine.ext import db

from djangomockup import models
from djangomockup.models.signals import pre_delete
from friday.auth import users


class Comment(models.Model):

    # The reference object on which this comment was posted. A comment can be attached to any
    # object in the datastore. The object is identified by its type (the model class name) and its
    # primary key.
    ref_type = db.StringProperty(required=True)
    ref_pk = db.StringProperty(required=True)

    # The content of the comment.
    content = db.TextProperty(required=True)

    # Metadata about the comment.
    author = db.ReferenceProperty(users.User, required=True)
    submit_date = db.DateTimeProperty(auto_now_add=True)

    schema_version = db.IntegerProperty(required=True, default=1)

    @classmethod
    def create(cls, ref_type, ref_pk, **kwargs):
        return cls(ref_type=ref_type, ref_pk=str(ref_pk), **kwargs)

    @classmethod
    def find(cls, ref_type, ref_pk, **kwargs):
        query = cls.objects.filter(ref_type=ref_type, ref_pk=str(ref_pk)).order_by("-submit_date")
        if kwargs.get("limit"):
            query.set_limit(kwargs["limit"])
        return query

    @classmethod
    def find_recent(cls, ref_type, **kwargs):
        query = cls.objects.filter(ref_type=ref_type).order_by("-submit_date")
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


def delete_related_comments(sender, **kwargs):
    if sender != Comment:
        try:
            instance = kwargs["instance"]
            deleted = Comment.delete_related(ref_type=sender.__name__, ref_pk=instance.pk)
            if deleted > 0:
                logging.info("%s related comments have been deleted successfully." % deleted)
        except Exception, exc:
            logging.error("Failed to delete related comments on instance: %s" % exc)
            logging.exception(exc)


pre_delete.connect(delete_related_comments)


# EOF
