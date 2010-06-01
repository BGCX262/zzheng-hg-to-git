#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-13.
# $Id$
#

import logging

from django import template

from friday.common.errors import ProgrammingError
from friday.apps.ilike.models import Fan, Fave


register = template.Library()


class WithFanOrFaveNode(template.Node):

    def __init__(self, model_class, instance, user, name, nodelist):
        self.model_class = model_class
        self.instance = instance
        self.user = user
        self.name = name
        self.nodelist = nodelist

    def render(self, context):
        instance = self.instance.resolve(context)
        user = self.user.resolve(context)
        if instance is not None and user is not None:
            fan_or_fave = self.model_class.get_unique(
                ref_type=instance.__class__.__name__,
                ref_pk=instance.pk,
                user=user
            )
        else:
            fan_or_fave = None
        context.push()
        context[self.name] = fan_or_fave
        output = self.nodelist.render(context)
        context.pop()
        return output


def with_fan_or_fave(model_class, parser, token):

    _END_TAGS = {
        Fan: ("endwithfan",),
        Fave: ("endwithfave",),
    }
    if model_class not in _END_TAGS:
        message = "Invalid model class %s in with fan or fave tag." % model_class.__name__
        logging.error(message)
        raise ProgrammingError(message)
    end_tags = _END_TAGS[model_class]

    bits = list(token.split_contents())
    if len(bits) != 5 or bits[3] != "as":
        raise TemplateSyntaxError("%r expected format is 'instance user as name'" % bits[0])
    instance = parser.compile_filter(bits[1])
    user = parser.compile_filter(bits[2])
    name = bits[4]
    nodelist = parser.parse(end_tags)
    parser.delete_first_token()
    return WithFanOrFaveNode(model_class, instance, user, name, nodelist)


@register.tag
def withfan(parser, token):
    return with_fan_or_fave(Fan, parser, token)


@register.tag
def withfave(parser, token):
    return with_fan_or_fave(Fave, parser, token)


# EOF
