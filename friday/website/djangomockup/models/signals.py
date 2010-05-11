#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-04-27.
# $Id$
#

from django.dispatch import Signal


pre_save = Signal(providing_args=["instance"])

post_save = Signal(providing_args=["instance", "created"])

pre_delete = Signal(providing_args=["instance"])

post_delete = Signal(providing_args=["instance"])


# EOF
