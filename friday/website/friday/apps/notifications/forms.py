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

from django import forms

from friday.common.errors import InvalidFormError
from friday.apps.notifications.models import Notification


class NotificationForm(forms.Form):

    subject = forms.CharField(max_length=128, required=True)
    message = forms.CharField(required=False, widget=forms.Textarea)
    recipients = forms.CharField(required=False, widget=forms.Textarea)

    def clean_recipients(self):
        recipients = self.cleaned_data["recipients"] \
                         .replace(",", "\n").replace(";", "\n") \
                         .splitlines()
        if not recipients:
            message = "Recipients are required."
            raise forms.ValidationError(message)
        return recipients

    def send(self, author):
        if not self.is_valid():
            raise InvalidFormError(self.errors)
        notification = Notification.send(
            category="TODO",
            subject=self.cleaned_data["subject"],
            message=self.cleaned_data["message"],
            author=author,
            recipients=self.cleaned_data["recipients"]
        )
        return notification


# EOF
