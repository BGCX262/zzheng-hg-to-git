#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#


import datetime
import logging
import random


__all__ = ("filter_key", "ord_to_key", "generate_key")


def _is_valid_key(s):
    if s.isdigit():
        return True
    elif s.lower() >= "a" and s.lower() <= "z":
        return True
    elif s == "-" or s == "." or s == "@" or s == "_":
        return True
    else:
        return False


def filter_key(name, min_length=None, reserved=None, force_lower=True):
    reserved = reserved or []
    pk = filter(_is_valid_key, str(name))
    if force_lower:
        pk = pk.lower()
    if min_length and len(pk) < min_length:
        raise ValueError("'%s' is too short." % pk)
    if pk in reserved:
        raise ValueError("'%s' is reserved." % pk)
    return pk


def ord_to_key(name, separator=None):
    separator = separator or "-"
    ord_list = ["%x" % ord(c) for c in name if not c.isspace()]
    return separator.join(ord_list)


def generate_key(max_rand=None):
    max_rand = max_rand or 0xFFFF
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    rand_suffix = "%4X" % random.randint(0, max_rand)
    return "%sX%s" % (timestamp, rand_suffix)


# EOF
