#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-20.
# $Id$
#

import logging

from django import forms
from django.forms.util import ErrorList

from friday.common.errors import ProgrammingError, InvalidFormError
from friday.apps.profiles.models import Profile


class ProfileForm(forms.Form):

    name = forms.CharField(required=True)
    biography = forms.CharField(required=False, widget=forms.Textarea)
    tel = forms.CharField(required=False)
    website = forms.URLField(required=False)

    def __init__(self, data=None, instance=None):
        self._instance = instance
        if instance:
            initial = {
                "name": instance.name,
                "biography": instance.biography,
                "tel": instance.tel,
                "website": instance.website,
            }
        else:
            initial = None
        super(ProfileForm, self).__init__(data=data, initial=initial)

    @property
    def instance(self):
        return self._instance

    def clean_website(self):
        return self.cleaned_data["website"] or None

    def clean_tel(self):
        return self.cleaned_data["tel"] or None

    def create(self, user):
        if self._instance is not None:
            message = "Failed to create profile: this form is bound to an existing profile."
            raise ProgrammingError(message)
        if not self.is_valid():
            raise InvalidFormError(self.errors)
        instance = Profile.create(user=user, **self.cleaned_data)
        instance.save()
        return instance

    def update(self):
        if self._instance is None:
            message = "Failed to update profile: this form is not bound to an profile."
            raise ProgrammingError(message)
        if not self.is_valid():
            raise InvalidFormError(self.errors)
        for name, value in self.cleaned_data.items():
            setattr(self._instance, name, value)
        self._instance.save()
        return self._instance


class AvatarForm(forms.Form):

    _AVATAR_SOURCE_CHOICES = (
        (Profile.GRAVATAR, "Take my avatar image from gravatar.com."),
        (Profile.IMAGE_URL, "Take my avatar image from a web URL."),
    )

    avatar_source = forms.ChoiceField(choices=_AVATAR_SOURCE_CHOICES, required=True)
    avatar_url = forms.URLField(required=False)

    def __init__(self, data=None, instance=None):
        if not instance:
            message = "Failed to create avatar form: this form must be bound to an profile."
            raise ProgrammingError(message)
        self._instance = instance
        initial = {
            "avatar_source": instance.avatar_source,
            "avatar_url": instance.avatar_url,
        }
        super(AvatarForm, self).__init__(data=data, initial=initial)

    @property
    def instance(self):
        return self._instance

    def clean_avatar_url(self):
        return self.cleaned_data["avatar_url"] or None

    def clean(self):
        logging.info("Called clean() ...")
        cleaned_data = self.cleaned_data
        avatar_source = cleaned_data.get("avatar_source")
        avatar_url = cleaned_data.get("avatar_url")
        if avatar_source == Profile.IMAGE_URL and not avatar_url:
            message = u"The avatar image URL is required."
            self._errors["avatar_url"] = ErrorList([message])
            del cleaned_data["avatar_url"]
        return cleaned_data

    def update(self):
        if not self.is_valid():
            raise InvalidFormError(self.errors)
        for name, value in self.cleaned_data.items():
            setattr(self._instance, name, value)
        self._instance.save()
        return self._instance


# EOF
