#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

import hashlib
import logging
import urllib

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from friday.auth import users
from friday.common.actions import Action
from friday.common.errors import BadRequestError, EntityNotFoundError
from friday.common.prompt import Prompt
from friday.apps.profiles.models import Profile
from friday.apps.profiles.forms import ProfileForm, AvatarForm


class BaseProfileAction(Action):

    def __init__(self, request, username):
        super(BaseProfileAction, self).__init__(request)
        self._user = users.get_user(username)

    def get_user(self):
        return self._user

    def get_profile(self, required=True):
        profile = Profile.get_unique(user=self._user)
        if not profile and required:
            message = "searched by user %s." % self._user.username
            raise EntityNotFoundError(Profile, message)
        return profile

    def update_data(self, data):
        data["profile"] = self.get_profile(required=False)
        data["user"] = self._user
        return super(BaseProfileAction, self).update_data(data)


class ViewProfile(BaseProfileAction):

    PAGE_URL_NAME = "friday.view_profile"
    PAGE_TEMPLATE = "profiles/view_profile.html"

    def get_page(self):
        data = self.update_data({})
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class EditProfile(BaseProfileAction):

    PAGE_URL_NAME = "friday.edit_profile"
    PAGE_TEMPLATE = "profiles/edit_profile.html"

    def _check_edit_access(self):
        if not self.current_user or self.current_user != self.get_user():
            message = "Current user cannot edit profile of %s." % self.get_user().username
            logging.error(message)
            raise BadRequestError(self.request, message)

    def get_page(self):
        self._check_edit_access()
        profile_form = ProfileForm(instance=self.get_profile(required=False))
        data = {"profile_form": profile_form}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        self._check_edit_access()
        profile_form = ProfileForm(
            data=self.request.POST,
            instance=self.get_profile(required=False)
        )
        try:
            if not profile_form.instance:
                profile = profile_form.create(self.get_user())
            else:
                profile = profile_form.update()
            message = "Profile of %s has been updated successfully." % profile.username
            logging.info(message)
            redirect_url = ViewProfile.get_page_url(username=profile.username)
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to create/update profile in datastore: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"profile_form": profile_form, "prompt": Prompt(error=message)}
            data = self.update_data(data)
            return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class ViewAvatar(BaseProfileAction):

    PAGE_URL_NAME = "friday.view_avatar"

    def get_page(self):
        profile = self.get_profile(required=False)
        if profile and profile.avatar_source == Profile.IMAGE_URL and profile.avatar_url:
            avatar_url = profile.avatar_url
        else:
            email_md5 = hashlib.md5(self.get_user().email).hexdigest().lower()
            avatar_url = "http://www.gravatar.com/avatar/%s" % email_md5
            avatar_url += "?" + urllib.urlencode({"s": 48, "d": "wavatar"})
        return HttpResponseRedirect(avatar_url)


class EditAvatar(BaseProfileAction):

    PAGE_URL_NAME = "friday.edit_avatar"
    PAGE_TEMPLATE = "profiles/edit_avatar.html"

    def _check_edit_access(self):
        if not self.current_user or self.current_user != self.get_user():
            message = "Current user cannot edit avatar of '%s'." % self.get_user().username
            logging.error(message)
            raise BadRequestError(self.request, message)

    def get_page(self):
        self._check_edit_access()
        avatar_form = AvatarForm(instance=self.get_profile())
        data = {"avatar_form": avatar_form}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        self._check_edit_access()
        avatar_form = AvatarForm(data=self.request.POST, instance=self.get_profile())
        try:
            profile = avatar_form.update()
            message = "Avatar of %s has been updated successfully." % profile.username
            logging.info(message)
            redirect_url = ViewProfile.get_page_url(username=profile.username)
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to update profile avatar in datastore: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"avatar_form": avatar_form, "prompt": Prompt(error=message)}
            data = self.update_data(data)
            return render_to_response(self.get_page_template(), data, RequestContext(self.request))


#---------------------------------------------------------------------------------------------------


def view_profile(request, username):
    return ViewProfile(request, username).process()


def edit_profile(request, username):
    return EditProfile(request, username).process()


def view_avatar(request, username):
    return ViewAvatar(request, username).process()


def edit_avatar(request, username):
    return EditAvatar(request, username).process()


# EOF
