#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-03.
# $Id$
#

from friday.apps.migration.models_v1 import *


def get_all_models():
    return (
        Activity,
        Attender,
        Comment,
        Group,
        Member,
        Notification,
        Profile,
        Resto,
        Tag,
    )


def get_model(model_name):
    for model_class in get_all_models():
        if model_class.__name__ == model_name:
            return model_class
    return None


# EOF
