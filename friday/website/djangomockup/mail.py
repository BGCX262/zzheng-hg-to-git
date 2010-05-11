#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2009-12-11.
# $Id$
#

from __future__ import absolute_import  # PEP 328

from google.appengine.api import mail


def is_email_valid(email):
    return mail.is_email_valid(email)


def send_mail(subject, message, from_email, recipient_list, fail_silently=False):
    mail.send_mail(
        sender=from_email,
        to=recipient_list,
        subject=subject,
        body=message
    )


# EOF
