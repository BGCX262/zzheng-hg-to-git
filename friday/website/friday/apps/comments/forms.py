#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-15.
# $Id$
#

from django import forms

from friday.common.errors import ProgrammingError, InvalidFormError
from friday.apps.comments.models import Comment


class CommentForm(forms.Form):

    content = forms.CharField(required=True, widget=forms.Textarea)

    def __init__(self, data=None, instance=None):
        self._instance = instance
        if instance:
            initial = {"content": instance.content}
        else:
            initial = None
        super(CommentForm, self).__init__(data=data, initial=initial)

    def create(self, ref_type, ref_pk, author):
        if self._instance is not None:
            message = "Failed to create comment: this form is bound to an existing comment."
            raise ProgrammingError(message)
        if not self.is_valid():
            raise InvalidFormError(self.errors)
        instance = Comment.create(
            ref_type=ref_type,
            ref_pk=ref_pk,
            author=author,
            **self.cleaned_data
        )
        instance.save()
        return instance


