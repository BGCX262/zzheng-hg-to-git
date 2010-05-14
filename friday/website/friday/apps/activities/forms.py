#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

import logging

from django import forms
from google.appengine.ext import db

from friday.common.errors import ProgrammingError, InvalidFormError
from friday.common.fields import GeoPtField
from friday.apps.activities.models import Activity


class ActivityForm(forms.Form):

    title = forms.CharField(required=True)
    content = forms.CharField(required=True, widget=forms.Textarea)
    date = forms.DateField(required=True)
    address = forms.CharField(required=False)
    city = forms.CharField(required=True)
    geo_pt = GeoPtField(required=False)
    places = forms.IntegerField(required=False)
    related_link = forms.URLField(required=False)
    is_closed = forms.BooleanField(required=False)

    def __init__(self, data=None, instance=None):
        self._instance = instance
        if instance:
            initial = {
                "title": instance.title,
                "content": instance.content,
                "date": instance.date,
                "address": instance.address,
                "city": instance.city,
                "geo_pt": instance.geo_pt,
                "places": instance.places,
                "related_link": instance.related_link,
                "is_closed": instance.is_closed,
            }
        else:
            initial = None
        super(ActivityForm, self).__init__(data=data, initial=initial)

    @property
    def instance(self):
        return self._instance

    def clean_address(self):
        return self.cleaned_data["address"] or None

    def clean_related_link(self):
        return self.cleaned_data["related_link"] or None

    def create(self, group, submitter):
        if self._instance is not None:
            message = "Failed to create activity: this form is bound to an existing activity."
            raise ProgrammingError(message)
        if not self.is_valid():
            raise InvalidFormError(self.errors)
        instance = Activity.create(group=group, submitter=submitter, **self.cleaned_data)
        instance.save()
        return instance

    def update(self):
        if self._instance is None:
            message = "Failed to update activity: this form is not bound to an activity."
            raise ProgrammingError(message)
        if not self.is_valid():
            raise InvalidFormError(self.errors)
        for name, value in self.cleaned_data.items():
            setattr(self._instance, name, value)
        self._instance.save()
        return self._instance


# EOF
