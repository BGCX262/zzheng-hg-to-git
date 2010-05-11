#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-05-03.
# $Id$
#

import logging

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from friday.auth import users
from friday.common.actions import Action
from friday.common.errors import BadRequestError
from friday.apps.migration.models import get_to_schema_version, get_all_models, get_model


class MigrateModel(Action):

    PAGE_URL_NAME = "friday.migrate_model"
    PAGE_TEMPLATE = "migration/migrate_model.html"

    AJAX_URL_NAME = "friday.migrate_model"
    AJAX_TEMPLATE = "migration/common/migrating.html"

    def _check_migrate_access(self):
        if not users.is_webmaster(self.current_user):
            message = "Current user cannot migrate model."
            raise BadRequestError(self.request, message)

    def get_page(self):
        all_models = {}
        for model_class in get_all_models():
            all_models[model_class.__name__] = model_class.has_old()
        data = {
            "to_schema_version": get_to_schema_version(),
            "all_models": all_models,
        }
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_ajax(self):
        self._check_migrate_access()
        model_name = self.request.POST.get("model_name")
        model_class = get_model(model_name)
        if not model_class:
            message = "Failed to find model class by name '%s'." % model_name
            raise BadRequestError(self.request, message)
        succeeded, failed = model_class.migrate()
        logging.info("Migrating %s: %s succeeded, %s failed." % (model_name, succeeded, failed))
        is_complete = not model_class.has_old()
        data = {
            "model_name": model_name,
            "succeeded": succeeded,
            "failed": failed,
            "is_complete": is_complete,
        }
        return data


#---------------------------------------------------------------------------------------------------


def migrate_model(request):
    return MigrateModel(request).process()


# EOF
