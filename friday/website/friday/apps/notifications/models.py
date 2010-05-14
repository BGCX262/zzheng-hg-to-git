#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-04-28.
# $Id$
#

import datetime
import logging

from google.appengine.ext import db

from djangomockup import models
from djangomockup import mail
from friday.auth import users
from friday.apps.notifications.signals import something_happened


class Notification(models.Model):

    _RESERVED_KEYS = ("create",)

    category = db.StringProperty(required=True)
    subject = db.StringProperty(required=True)
    message = db.TextProperty(required=True)
    author = db.ReferenceProperty(users.User, required=True)
    recipients = db.ListProperty(db.Email, required=True, default=[])
    send_date = db.DateTimeProperty(required=False)

    schema_version = db.IntegerProperty(required=True, default=1)

    def __unicode__(self):
        return unicode(self.subject)

    @classmethod
    def get_unique(cls, id):
        try:
            instance = cls.objects.get(id=id)
        except cls.DoesNotExist:
            instance = None
        return instance

    @classmethod
    def create(cls, **kwargs):
        # Convert recipients string list to a list of db.Email objects.
        recipients = []
        for recipient_email in kwargs["recipients"]:
            if mail.is_email_valid(recipient_email):
                recipients.append(db.Email(recipient_email))
            else:
                logging.warning("Invalid email address ignored: %s" % recipient_email)
        kwargs["recipients"] = recipients
        # Create an instance.
        return cls(**kwargs)

    @classmethod
    def send(cls, **kwargs):
        notification = cls.create(**kwargs)
        mail.send_mail(
            subject=notification.subject,
            message=notification.message,
            from_email=notification.author.email,
            recipient_list=notification.recipients
        )
        notification.send_date = datetime.datetime.now()
        notification.save()
        return notification

    @classmethod
    def find(cls, **kwargs):
        query = cls.objects.all()
        if "category" in kwargs:
            query = query.filter(category=kwargs["category"])
        if "author" in kwargs:
            query = query.filter(author=kwargs["author"])
        if "recipient" in kwargs:
            query = query.filter(recipients=db.Email(kwargs["recipient"]))
        query = query.order_by(kwargs.get("order_by") or "-send_date")
        if kwargs.get("limit"):
            query = query[:kwargs["limit"]]
        return query


def send_notification(sender, **kwargs):
    try:
        kwargs["message"] = kwargs["message"].strip()
        subject = kwargs.get("subject") or kwargs["message"].splitlines()[0]
        Notification.send(
            category=unicode(sender),
            subject=subject,
            message=kwargs["message"],
            author=kwargs["author"],
            recipients=kwargs["recipients"]
        )
    except Exception, exc:
        logging.error("Failed to send notification: %s" % exc)
        logging.exception(exc)


something_happened.connect(send_notification)


# EOF
