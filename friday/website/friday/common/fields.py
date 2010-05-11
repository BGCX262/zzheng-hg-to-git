#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

from django import forms
from google.appengine.ext import db


class GeoPtField(forms.Field):

    def __init__(self, *args, **kwargs):
        super(GeoPtField, self).__init__(*args, **kwargs)

    def clean(self, value):
        """
        Returns a db.GeoPt object for valid values, and None for empty values.
        """
        super(GeoPtField, self).clean(value)
        if not self.required and not value:
            return None
        try:
            geo_pt = value.split(",")
            if len(geo_pt) != 2:
                raise forms.ValidationError(self.error_messages["invalid"])
            lat = float(geo_pt[0])
            lon = float(geo_pt[1])
            value = db.GeoPt(lat=lat, lon=lon)
        except (TypeError, ValueError):
            raise forms.ValidationError(self.error_messages["invalid"])
        return value


# EOF
