#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-13.
# $Id$
#

from django import template

from friday.apps.ilike.models import Fan


register = template.Library()


class WithFanNode(template.Node):

    def __init__(self, instance, user, name, nodelist):
        self.instance = instance
        self.user = user
        self.name = name
        self.nodelist = nodelist

    def render(self, context):
        instance = self.instance.resolve(context)
        user = self.user.resolve(context)
        if instance is not None and user is not None:
            fan = Fan.get_unique(
                ref_type=instance.__class__.__name__,
                ref_pk=instance.pk,
                user=user
            )
        else:
            fan = None
        context.push()
        context[self.name] = fan
        output = self.nodelist.render(context)
        context.pop()
        return output


@register.tag
def withfan(parser, token):
    """
    Usage::

        {% withfan instance current_user as fan %}
            {% if fan %}
                User {{ current_user }} is a fan of {{ instance }}
            {% else %}
                User {{ current_user }} is not a fan of {{ instance }}
            {% endif %}
        {% endwithfan %}
    """
    bits = list(token.split_contents())
    if len(bits) != 5 or bits[3] != "as":
        raise TemplateSyntaxError("%r expected format is 'instance user as name'" % bits[0])
    instance = parser.compile_filter(bits[1])
    user = parser.compile_filter(bits[2])
    name = bits[4]
    nodelist = parser.parse(("endwithfan",))
    parser.delete_first_token()
    return WithFanNode(instance, user, name, nodelist)


# EOF
