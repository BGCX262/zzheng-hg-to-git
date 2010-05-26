#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

import logging

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from friday.auth import users
from friday.common.actions import Action
from friday.common.errors import BadRequestError, EntityNotFoundError
from friday.common.prompt import Prompt

from friday.apps.groups.models import Group, Member
from friday.apps.groups.access import GroupAccess
from friday.apps.groups.forms import GroupForm, PrettifyGroupForm, JoinGroupForm, \
                                     ReviewMemberForm, MemberForm


class ViewAllGroups(Action):

    PAGE_URL_NAME = "friday.view_all_groups"
    PAGE_TEMPLATE = "groups/view_all_groups.html"

    def get_page(self):
        data = self.update_data({"groups": Group.find_all()})
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class CreateGroup(Action):

    PAGE_URL_NAME = "friday.create_group"
    PAGE_TEMPLATE = "groups/create_group.html"

    def _check_create_access(self):
        if not users.is_webmaster(self.current_user):
            message = "Only webmaster can create new groups."
            logging.error(message)
            raise BadRequestError(self.request, message)

    def get_page(self):
        self._check_create_access()
        data = {"group_form": GroupForm()}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        self._check_create_access()
        group_form = GroupForm(data=self.request.POST)
        try:
            group = group_form.create(creator=self.current_user)
            message = "Group %s has been created successfully." % group.uid
            logging.info(message)
            redirect_url = ViewGroup.get_page_url(group_uid=group.uid)
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to create group in datastore: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"group_form": group_form, "prompt": Prompt(error=message)}
            data = self.update_data(data)
            return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class BaseGroupAction(Action):

    def __init__(self, request, group_uid):
        super(BaseGroupAction, self).__init__(request)
        self.group_uid = group_uid

    def get_group(self):
        group = Group.get_unique(uid=self.group_uid)
        if not group:
            message = "searched by group uid %s." % self.group_uid
            raise EntityNotFoundError(Group, message)
        return group

    def get_group_access(self):
        return GroupAccess(self.get_group(), self.current_user)

    def update_data(self, data):
        data["group"] = self.get_group()
        data["group_access"] = self.get_group_access()
        return super(BaseGroupAction, self).update_data(data)


class ViewGroup(BaseGroupAction):

    PAGE_URL_NAME = "friday.view_group"
    PAGE_TEMPLATE = "groups/view_group.html"

    def get_page(self):
        pending_members = Member.find_by_group(
            group=self.get_group(),
            is_approved=False,
            order_by="-join_date"
        )
        new_members = Member.find_by_group(
            group=self.get_group(),
            is_approved=True,
            order_by="-join_date",
            limit=7
        )
        data = {"pending_members": pending_members, "new_members": new_members}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class EditGroup(BaseGroupAction):

    PAGE_URL_NAME = "friday.edit_group"
    PAGE_TEMPLATE = "groups/edit_group.html"

    def _check_edit_access(self):
        if not self.get_group_access().can_administrate():
            message = "Current user cannot edit group %s." % self.get_group().uid
            logging.error(message)
            raise BadRequestError(self.request, message)

    def get_page(self):
        self._check_edit_access()
        group_form = GroupForm(instance=self.get_group())
        data = {"group_form": group_form}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        self._check_edit_access()
        group_form = GroupForm(data=self.request.POST, instance=self.get_group())
        try:
            group = group_form.update()
            message = "Group %s has been updated successfully." % group.uid
            logging.info(message)
            redirect_url = ViewGroup.get_page_url(group_uid=group.uid)
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to update group in datastore: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"group_form": group_form, "prompt": Prompt(error=message)}
            data = self.update_data(data)
            return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class PrettifyGroup(BaseGroupAction):

    PAGE_URL_NAME = "friday.prettify_group"
    PAGE_TEMPLATE = "groups/prettify_group.html"

    def _check_edit_access(self):
        if not self.get_group_access().can_administrate():
            message = "Current user cannot prettify group %s." % self.get_group().uid
            logging.error(message)
            raise BadRequestError(self.request, message)

    def get_page(self):
        self._check_edit_access()
        prettify_group_form = PrettifyGroupForm(instance=self.get_group())
        data = {"prettify_group_form": prettify_group_form}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        self._check_edit_access()
        prettify_group_form = PrettifyGroupForm(data=self.request.POST, instance=self.get_group())
        try:
            group = prettify_group_form.update()
            message = "Group %s has been updated successfully." % group.uid
            logging.info(message)
            redirect_url = ViewGroup.get_page_url(group_uid=group.uid)
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to update group in datastore: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"prettify_group_form": prettify_group_form, "prompt": Prompt(error=message)}
            data = self.update_data(data)
            return render_to_response(self.PAGE_TEMPLATE, data, RequestContext(self.request))


class JoinGroup(BaseGroupAction):

    PAGE_URL_NAME = "friday.join_group"
    PAGE_TEMPLATE = "groups/join_group.html"

    def _check_join_access(self):
        if not self.get_group_access().can_join():
            message = "Current user cannot join group %s." % self.get_group().uid
            logging.error(message)
            raise BadRequestError(self.request, message)

    def get_page(self):
        self._check_join_access()
        data = {"join_group_form": JoinGroupForm()}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        self._check_join_access()
        join_group_form = JoinGroupForm(data=self.request.POST)
        try:
            member = join_group_form.create(user=self.current_user, group=self.get_group())
            message = "Member '%s' has been created successfully." % member.pk
            logging.info(message)
            redirect_url = ViewGroup.get_page_url(group_uid=self.get_group().uid)
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to create member in datastore: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"join_group_form": join_group_form, "prompt": Prompt(error=message)}
            data = self.update_data(data)
            return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class ViewMembers(BaseGroupAction):

    PAGE_URL_NAME = "friday.view_members"
    PAGE_TEMPLATE = "groups/view_members.html"

    def get_page(self):
        order_by = self.request.GET.get("order_by") or "-join_date"
        cursor = self.request.GET.get("cursor") or None
        pending_members = Member.find_by_group(
            group=self.get_group(),
            is_approved=False,
            order_by=order_by
        )
        approved_members = Member.find_by_group(
            group=self.get_group(),
            is_approved=True,
            order_by=order_by,
            cursor=cursor,
            limit=20
        )
        data = {
            "pending_members": pending_members,
            "approved_members": approved_members,
            "ordered_by": order_by,
        }
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class BaseMemberAction(BaseGroupAction):

    def __init__(self, request, group_uid, username):
        super(BaseMemberAction, self).__init__(request, group_uid)
        self._username = username
        self._user = users.get_user(username, create=False)

    def get_user(self):
        if not self._user:
            message = "searched by username %s." % self._username
            raise EntityNotFoundError(users.User, message)
        return self._user

    def get_member(self):
        member = Member.get_unique(group=self.get_group(), user=self.get_user())
        if not member:
            message = "searched by user %s." % self.get_user().username
            raise EntityNotFoundError(Member, message)
        return member

    def update_data(self, data):
        data["member"] = self.get_member()
        return super(BaseMemberAction, self).update_data(data)


class ReviewMember(BaseMemberAction):

    PAGE_URL_NAME = "friday.review_member"
    PAGE_TEMPLATE = "groups/review_member.html"

    def _check_review_access(self):
        if self.get_member().is_approved:
            message = "Member '%s' does not need to be reviewed." % self.get_member().username
            logging.error(message)
            raise BadRequestError(self.request, message)
        if not self.get_group_access().can_moderate():
            message = "Current user cannot review member '%s'." % self.get_member().username
            logging.error(message)
            raise BadRequestError(self.request, message)

    def get_page(self):
        self._check_review_access()
        review_member_form = ReviewMemberForm(instance=self.get_member())
        data = {"review_member_form": review_member_form}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        self._check_review_access()
        review_member_form = ReviewMemberForm(data=self.request.POST, instance=self.get_member())
        try:
            member = review_member_form.update()
            message = "Member %s has been updated successfully." % member.username
            logging.info(message)
            redirect_url = ViewMembers.get_page_url(group_uid=self.get_group().uid)
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to update member in datastore: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"review_member_form": review_member_form, "prompt": Prompt(error=message)}
            data = self.update_data(data)
            return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class EditMember(BaseMemberAction):

    PAGE_URL_NAME = "friday.edit_member"
    PAGE_TEMPLATE = "groups/edit_member.html"

    def _check_edit_access(self):
        if not self.get_group_access().can_administrate():
            message = "Current user cannot edit member '%s'." % self.get_member().username
            logging.error(message)
            raise BadRequestError(self.request, message)

    def get_page(self):
        self._check_edit_access()
        member_form = MemberForm(instance=self.get_member())
        data = {"member_form": member_form}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        self._check_edit_access()
        member_form = MemberForm(data=self.request.POST, instance=self.get_member())
        try:
            member = member_form.update()
            message = "Member '%s' has been updated successfully." % member.username
            logging.info(message)
            redirect_url = ViewMembers.get_page_url(group_uid=self.get_group().uid)
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to update member in datastore: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"member_form": member_form, "prompt": Prompt(error=message)}
            data = self.update_data(data)
            return render_to_response(self.get_page_template(), data, RequestContext(self.request))


#---------------------------------------------------------------------------------------------------


def groups_home(request):
    redirect_url = ViewAllGroups.get_page_url()
    return HttpResponseRedirect(redirect_url)


def view_all_groups(request):
    return ViewAllGroups(request).process()


def create_group(request):    
    return CreateGroup(request).process()


def view_group(request, group_uid):
    return ViewGroup(request, group_uid).process()


def edit_group(request, group_uid):
    return EditGroup(request, group_uid).process()


def prettify_group(request, group_uid):
    return PrettifyGroup(request, group_uid).process()


def join_group(request, group_uid):
    return JoinGroup(request, group_uid).process()


def view_members(request, group_uid):
    return ViewMembers(request, group_uid).process()


def review_member(request, group_uid, username):
    return ReviewMember(request, group_uid, username).process()


def edit_member(request, group_uid, username):
    return EditMember(request, group_uid, username).process()


# EOF
