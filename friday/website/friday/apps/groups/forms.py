#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

from django import forms

from friday.common.errors import ProgrammingError, InvalidFormError
from friday.apps.groups.models import Group, Member


class GroupForm(forms.Form):

    uid = forms.CharField(max_length=32, required=True)
    name = forms.CharField(max_length=128, required=True)
    slogan = forms.CharField(max_length=255, required=False)
    description = forms.CharField(required=False, widget=forms.Textarea)
    website = forms.URLField(required=False)
    google_group = forms.CharField(required=False)

    def __init__(self, data=None, instance=None):
        self._instance = instance
        if instance:
            initial = {
                "uid": instance.uid,
                "name": instance.name,
                "slogan": instance.slogan,
                "description": instance.description,
                "website": instance.website,
                "google_group": instance.google_group,
            }
        else:
            initial = None
        super(GroupForm, self).__init__(data=data, initial=initial)

    @property
    def instance(self):
        return self._instance

    def clean_website(self):
        return self.cleaned_data["website"] or None

    def create(self, creator):
        if self._instance is not None:
            message = "Failed to create group: this form is bound to an existing group."
            raise ProgrammingError(message)
        if not self.is_valid():
            raise InvalidFormError(self.errors)
        instance = Group.create(creator=creator, **self.cleaned_data)
        instance.save()
        return instance

    def update(self):
        if self._instance is None:
            message = "Failed to update group: this form is not bound to a group."
            raise ProgrammingError(message)
        if not self.is_valid():
            raise InvalidFormError(self.errors)
        if self._instance.uid != self.cleaned_data["uid"]:
            message = "Group uid is read-only, and cannot be updated."
            raise ProgrammingError(message)
        for name, value in self.cleaned_data.items():
            if name != "uid":
                setattr(self._instance, name, value)
        self._instance.save()
        return self._instance


class PrettifyGroupForm(forms.Form):

    background_url = forms.URLField(required=False)
    logo_icon_url = forms.URLField(required=False)

    def __init__(self, data=None, instance=None):
        if not instance:
            message = "Failed to create prettify group form: this form must be bound to a group."
            raise ProgrammingError(message)
        self._instance = instance
        initial = {
            "background_url": instance.background_url,
            "logo_icon_url": instance.logo_icon_url,
        }
        super(PrettifyGroupForm, self).__init__(data=data, initial=initial)

    @property
    def instance(self):
        return self._instance

    def clean_background_url(self):
        return self.cleaned_data["background_url"] or None

    def clean_logo_icon_url(self):
        return self.cleaned_data["logo_icon_url"] or None

    def update(self):
        if not self.is_valid():
            raise InvalidFormError(self.errors)
        for name, value in self.cleaned_data.items():
            setattr(self._instance, name, value)
        self._instance.save()
        return self._instance


class JoinGroupForm(forms.Form):

    request_message = forms.CharField(required=False, widget=forms.Textarea)

    def create(self, user, group):
        if not self.is_valid():
            raise InvalidFormError(self.errors)
        instance = Member.create(user=user, group=group, **self.cleaned_data)
        instance.save()
        return instance


class ReviewMemberForm(forms.Form):

    _APPROVE = "approve"
    _REJECT = "reject"
    _DECIDE_LATER = "decide_later"

    _REVIEW_CHOICES = (
        (_APPROVE, "Approve the request and add the user to this group."),
        (_REJECT, "Reject the request and remove the user from this group."),
        (_DECIDE_LATER, "Decide later."),
    )

    review = forms.ChoiceField(choices=_REVIEW_CHOICES, required=True, widget=forms.RadioSelect)

    def __init__(self, data=None, instance=None):
        if not instance:
            message = "Failed to create review member form: this form must be bound to a member."
            raise ProgrammingError(message)
        elif instance.is_approved:
            message = "Failed to create review member form: member is already approved."
            raise ProgrammingError(message)
        self._instance = instance
        initial = {"review": ReviewMemberForm._APPROVE}
        super(ReviewMemberForm, self).__init__(data=data, initial=initial)

    @property
    def instance(self):
        return self._instance

    def update(self):
        if not self.is_valid():
            raise InvalidFormError(self.errors)
        review = self.cleaned_data["review"]
        if review == ReviewMemberForm._APPROVE:
            self._instance.is_approved = True
            self._instance.save()
        elif review == ReviewMemberForm._REJECT:
            self._instance.delete()
        else:
            pass
        return self._instance


class MemberForm(forms.Form):

    _ROLE_CHOICES = (
        (Member.ADMINISTRATOR, "Administrator - administrator can change group settings"),
        (Member.MODERATOR, "Moderator - moderator can approve pending members"),
        (Member.MEMBER, "Member - member can view the group contents"),
    )

    role = forms.ChoiceField(choices=_ROLE_CHOICES, required=True, widget=forms.RadioSelect)
    remove_member = forms.BooleanField(required=False)

    def __init__(self, data=None, instance=None):
        self._instance = instance
        initial = {"remove_member": False}
        if instance:
            initial["role"] = instance.role
        super(MemberForm, self).__init__(data=data, initial=initial)

    @property
    def instance(self):
        return self._instance

    def update(self):
        if self._instance is None:
            message = "Failed to update member: this form is not bound to a member."
            raise ProgrammingError(message)
        if not self.is_valid():
            raise InvalidFormError(self.errors)
        if not self.cleaned_data["remove_member"]:
            self._instance.role = self.cleaned_data["role"]
            self._instance.save()
        else:
            self._instance.delete()
        return self._instance


# EOF
