#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-11.
# $Id$
#

from django import forms

from friday.auth import users
from friday.common.errors import ProgrammingError, InvalidFormError
from friday.apps.halloffame.models import Inductee


class InducteeForm(forms.Form):

    uid = forms.CharField(max_length=32, required=True)
    name = forms.CharField(max_length=64, required=True)
    aka = forms.CharField(max_length=64, required=False)
    user = forms.CharField(max_length=64, required=True)
    summary = forms.CharField(max_length=128, required=True)
    biography = forms.CharField(required=True, widget=forms.Textarea)

    def __init__(self, data=None, instance=None):
        self._instance = instance
        if instance:
            initial = {
                "uid": instance.uid,
                "name": instance.name,
                "aka": instance.aka,
                "user": instance.user.email,
                "summary": instance.summary,
                "biography": instance.biography,
            }
        else:
            initial = None
        super(InducteeForm, self).__init__(data=data, initial=initial)

    @property
    def instance(self):
        return self._instance

    def clean_user(self):
        username_or_email = self.cleaned_data["user"]
        user = users.get_user(username_or_email, create=False)
        if user is None:
            message = "User %s cannot be found." % username_or_email
            raise forms.ValidationError(message)
        return user

    def create(self, group):
        if self._instance is not None:
            message = "Failed to create inductee: this form is bound to an existing instance."
            raise ProgrammingError(message)
        if not self.is_valid():
            raise InvalidFormError(self.errors)
        instance = Inductee.create(group=group, **self.cleaned_data)
        instance.save()
        return instance

    def update(self):
        if self._instance is None:
            message = "Failed to update inductee: this form is not bound to an instance."
            raise ProgrammingError(message)
        if not self.is_valid():
            raise InvalidFormError(self.errors)
        if self._instance.uid != self.cleaned_data["uid"]:
            message = "Inductee uid is read-only, and cannot be updated."
            raise ProgrammingError(message)
        for name, value in self.cleaned_data.items():
            if name != "uid":
                setattr(self._instance, name, value)
        self._instance.save()
        return self._instance


class InducteePhotoForm(forms.Form):

    photo = forms.FileField(required=False)
    delete_photo = forms.BooleanField(required=False, initial=False)

    def update(self, inductee):
        if not self.is_valid():
            raise InvalidFormError(self.errors)
        if self.cleaned_data["delete_photo"]:
            inductee.photo_type = None
            inductee.photo_data = None
        photo = self.cleaned_data["photo"]
        if photo:
            inductee.photo_type = photo.content_type
            inductee.photo_data = photo.read()
        inductee.save()
        return inductee


# EOF
