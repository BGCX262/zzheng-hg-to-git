#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

import csv
import datetime
import logging

from django import forms
from django.conf import settings

from friday.auth import users
from friday.common.errors import ProgrammingError, InvalidFormError
from friday.apps.groups.models import Group, Member
from friday.apps.restos.models import Resto


class DatabaseImportForm(forms.Form):

    csv_file = forms.FileField(required=True)

    def import_to_database(self):
        if not self.is_valid():
            raise InvalidFormError(self.errors)
        csv_file = self.cleaned_data["csv_file"]
        csv_data = csv.reader(csv_file)
        imported, ignored, failed = 0, 0, 0
        for csv_row in csv_data:
            try:
                csv_row = [unicode(cell, "utf-8") for cell in csv_row]
                instance = self.create_instance(csv_row)
                if instance is not None:
                    instance.save()
                    imported += 1
                else:
                    ignored += 1
            except Exception, exc:
                logging.error("Failed to import CSV row to database: %s" % exc)
                logging.error("--> %s" % csv_row)
                logging.exception(exc)
                failed += 1
        return imported, ignored, failed

    def create_instance(self, csv_row):
        raise NotImplementedError("create_instance() should be implemented by sub-classes.")


class ImportMembersForm(DatabaseImportForm):

    _EMAIL_DOMAIN = getattr(settings, "MY_EMAIL_DOMAIN", None)

    group = forms.CharField(max_length=64, required=True)

    def clean_group(self):
        group_uid = self.cleaned_data["group"]
        group = Group.get_unique(uid=group_uid)
        if group is None:
            message = "Group %s cannot be found." % group_uid
            raise forms.ValidationError(message)
        return group

    def create_instance(self, csv_row):
        # Ignore all emails that are not in the supported domain.
        email = csv_row[0].lower()
        if not email.endswith("@" + self._EMAIL_DOMAIN):
            return None
        # Ignore all members that already exist.
        group = self.cleaned_data["group"]
        user = users.get_user(email)
        if Member.get_unique(group=group, user=user) is not None:
            return None
        # Create a new Member instance.
        if csv_row[2] == "manager" or csv_row[2] == "owner":
            role = Member.MODERATOR
        else:
            role = Member.MEMBER
        join_date = datetime.date(int(csv_row[6]), int(csv_row[7]), int(csv_row[8]))
        return Member.create(
            user=user,
            group=group,
            role=role,
            join_date=join_date,
            is_approved=True
        )

    def import_members(self):
        if not self._EMAIL_DOMAIN:
            message = "Failed to import members: email domain not defeind in settings."
            raise ProgrammingError(message)
        return self.import_to_database()


class ImportRestosForm(DatabaseImportForm):

    submitter = users.get_user("heavyzheng")
    categories = [category for category, display in Resto.CATEGORIES]

    def create_instance(self, csv_row):
        name = csv_row[0].strip()
        category = csv_row[7].strip()
        if category not in self.categories:
            return None
        city = csv_row[3].strip()
        if city != u"巴黎":
            return None
        city = u"Paris"
        address = csv_row[1].strip()
        route = csv_row[2].strip()
        tel_1 = csv_row[4].strip() or None
        resto = Resto.create(
            name=name,
            category=category,
            address=address,
            route=route,
            city=city,
            tel_1=tel_1,
            submitter=self.submitter
        )
        return resto

    def import_restos(self):
        return self.import_to_database()


# EOF
