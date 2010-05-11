#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created on 2009-11-18.
# $Id$
#

"""
To use filters defined in this module, add the following line to the templates:
    {% load fridayfilters %}
"""


import datetime
import hashlib
import logging
import urllib

from django import template


register = template.Library()


@register.filter
def uniqueid(value):
    return "%x" % id(value)


@register.filter
def multiply(value, arg):
    """
    Multiplies the value (as an integer) by arg.
    """
    if isinstance(value, int) or isinstance(value, float):
        return value * arg
    else:
        return u"%s x %s" % (value, arg)


@register.filter
def prettify_datetime(value):
    """
    Prettifies a date or a datetime, returns a humain read-able string.
    """

    # Check the value argument type, and calculate dt.
    if isinstance(value, datetime.datetime):
        dt = datetime.datetime.now() - value
    elif isinstance(value, datetime.date):
        dt = datetime.date.today() - value
    else:
        return value

    # Check if value is in the future or in the past, and abs(dt).
    is_past = (dt >= datetime.timedelta(0))
    dt = abs(dt)

    # Generate the basic pretty string for value.
    time_units = (
        ("year", dt.days // 365),
        ("month", (dt.days % 365) // 30),
        ("day", dt.days % 30),
        ("hour", dt.seconds // 3600),
        ("minute", (dt.seconds % 3600) // 60),
    )
    pretty_str = None
    for unit, amount in time_units:
        if amount > 0:
            pretty_str = "%d %s" % (amount, unit)
            if amount > 1:
                pretty_str += "s"
            break

    # Post-process the basic pretty string.
    if is_past:
        if not pretty_str:
            pretty_str = "just now"
        else:
            pretty_str += " ago"
    else:
        if not pretty_str:
            pretty_str = "right now"
        else:
            pretty_str = "in " + pretty_str

    # Return the final result.
    return pretty_str


@register.filter
def safe_email(value):
    if not isinstance(value, basestring):
        return value
    else:
        parts = value.split("@")
        if len(parts) == 2:
            parts[1] = parts[1].replace(".", " [D0T] ")
        return " [at] ".join(parts)


@register.filter
def gravatar(value):
    if not isinstance(value, basestring):
        return value
    else:
        email_md5 = hashlib.md5(value.lower()).hexdigest().lower()
        gravatar_url = "http://www.gravatar.com/avatar/%s" % email_md5
        gravatar_url += "?" + urllib.urlencode({"s": 48, "d": "wavatar"})
        return gravatar_url


# EOF
