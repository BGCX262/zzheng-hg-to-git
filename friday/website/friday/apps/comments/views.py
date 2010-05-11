#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-15.
# $Id$
#

import logging

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

from friday.common.errors import BadRequestError, InvalidFormError
from friday.common.prompt import Prompt
from friday.common.actions import Action
from friday.apps.comments.models import Comment
from friday.apps.comments.forms import CommentForm


class BaseCommentsAction(Action):

    def __init__(self, request, ref_type, ref_pk):
        super(BaseCommentsAction, self).__init__(request)
        self.ref_type = ref_type
        self.ref_pk = ref_pk

    def update_data(self, data):
        data["ref_type"] = self.ref_type
        data["ref_pk"] = self.ref_pk
        return super(BaseCommentsAction, self).update_data(data)


class ViewComments(BaseCommentsAction):

    AJAX_URL_NAME = "friday.view_comments"
    AJAX_TEMPLATE = "comments/common/comments.html"

    def update_data(self, data):
        comments = Comment.find(ref_type=self.ref_type, ref_pk=self.ref_pk)
        data["comments"] = comments
        return super(ViewComments, self).update_data(data)

    def get_ajax(self):
        if self.current_user:
            comment_form = CommentForm()
        else:
            comment_form = None
        return {"comment_form": comment_form}

    def post_ajax(self):
        if not self.current_user:
            message = "Anonymous user cannot add comment"
            raise BadRequestError(self.request, message)
        comment_form = CommentForm(data=self.request.POST)
        try:
            comment = comment_form.create(
                ref_type=self.ref_type,
                ref_pk=self.ref_pk,
                author=self.current_user
            )
            return {"comment_form": CommentForm()}
        except Exception, exc:
            message = "Failed to add comment: %s" % exc
            logging.error(message)
            logging.exception(exc)
            return {"ajax_prompt": Prompt(error=message), "comment_form": comment_form}


#---------------------------------------------------------------------------------------------------


def view_comments(request, ref_type, ref_pk):
    return ViewComments(request, ref_type, ref_pk).process()


# EOF
