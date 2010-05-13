#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-18.
# $Id$
#

import logging

from django import forms

from friday.common.errors import ProgrammingError, InvalidFormError
from friday.common.fields import GeoPtField
from friday.apps.restos.models import Resto, Dish


class RestoForm(forms.Form):

    name = forms.CharField(required=True)
    description = forms.CharField(required=False, widget=forms.Textarea)

    category = forms.ChoiceField(choices=Resto.CATEGORIES, required=True)

    address = forms.CharField(required=True)
    city = forms.CharField(required=True)
    geo_pt = GeoPtField(required=False)
    post_code = forms.CharField(required=False)
    route = forms.CharField(required=False)

    tel_1 = forms.CharField(required=False)
    tel_2 = forms.CharField(required=False)
    website = forms.URLField(required=False)

    hours_1 = forms.CharField(required=False)
    hours_2 = forms.CharField(required=False)
    hours_3 = forms.CharField(required=False)
    places = forms.IntegerField(required=False)

    def __init__(self, data=None, instance=None):
        self._instance = instance
        if instance:
            initial = {
                "name": instance.name,
                "description": instance.description,
                "category": instance.category,
                "address": instance.address,
                "city": instance.city,
                "geo_pt": instance.geo_pt,
                "post_code": instance.post_code,
                "route": instance.route,
                "tel_1": instance.tel_1,
                "tel_2": instance.tel_2,
                "website": instance.website,
                "hours_1": instance.hours_1,
                "hours_2": instance.hours_2,
                "hours_3": instance.hours_3,
                "places": instance.places,
            }
        else:
            initial = None
        super(RestoForm, self).__init__(data=data, initial=initial)

    @property
    def instance(self):
        return self._instance

    def clean_website(self):
        return self.cleaned_data["website"] or None

    def clean_tel_1(self):
        return self.cleaned_data["tel_1"] or None

    def clean_tel_2(self):
        return self.cleaned_data["tel_2"] or None

    def create(self, submitter):
        if self._instance is not None:
            message = "Failed to create resto: this form is bound to an existing resto."
            raise ProgrammingError(message)
        if not self.is_valid():
            raise InvalidFormError(self.errors)
        instance = Resto.create(submitter=submitter, **self.cleaned_data)
        instance.save()
        return instance

    def update(self, updater):
        if self._instance is None:
            message = "Failed to update resto: this form is not bound to an resto."
            raise ProgrammingError(message)
        if not self.is_valid():
            raise InvalidFormError(self.errors)
        for name, value in self.cleaned_data.items():
            setattr(self._instance, name, value)
        self._instance.updater = updater
        self._instance.save()
        return self._instance


class RestoTagForm(forms.Form):

    names = forms.CharField(required=False)

    def add_tags(self, resto):
        if not self.is_valid():
            raise InvalidFormError(self.errors)
        resto.add_tags(self.cleaned_data["names"])
        resto.save()
        return resto


class DishForm(forms.Form):

    name = forms.CharField(required=True)
    description = forms.CharField(required=False, widget=forms.Textarea)
    photo_url = forms.URLField(required=False)
    is_spicy = forms.BooleanField(required=False)
    is_vegetarian = forms.BooleanField(required=False)
    price = forms.CharField(required=False)

    def clean_photo_url(self):
        return self.cleaned_data["photo_url"] or None

    def create(self, resto):
        if not self.is_valid():
            raise InvalidFormError(self.errors)
        instance = Dish.create(resto=resto, **self.cleaned_data)
        instance.save()
        return instance


# EOF
