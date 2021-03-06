#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-18.
# $Id$
#

import hashlib
import logging
import random
import urllib

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from friday.common.errors import BadRequestError, InvalidFormError, EntityNotFoundError
from friday.common.prompt import Prompt
from friday.common.actions import Action
from friday.apps.comments.models import Comment
from friday.apps.tagging.models import Tag
from friday.apps.restos.models import Resto, Dish
from friday.apps.restos.access import RestoAccess
from friday.apps.restos.forms import RestoForm, RestoTagForm, DishForm


class RestosHome(Action):

    PAGE_URL_NAME = "friday.restos_home"
    PAGE_TEMPLATE = "restos/home.html"

    def get_page(self):
        # Find newly added restos (randomly select 4 out of 10).
        newly_added_restos = list(Resto.find(order_by="-update_date", limit=10))
        random.shuffle(newly_added_restos)
        newly_added_restos = newly_added_restos[:4]
        # Find newly commented restos (a list of 2-tuple with resto and comment).
        new_comments = Comment.find_recent(ref_type=Resto.__name__, limit=4)
        newly_commented_restos = []
        for comment in new_comments:
            resto = Resto.get_unique(id=int(comment.ref_pk))
            if resto:
                newly_commented_restos.append((resto, comment))
        # Render the response.
        data = {
            "categories": Resto.CATEGORIES,
            "newly_added_restos": newly_added_restos,
            "newly_commented_restos": newly_commented_restos,
        }
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class ViewAllRestos(Action):

    PAGE_URL_NAME = "friday.view_all_restos"
    PAGE_TEMPLATE = "restos/view_all_restos.html"

    def get_page(self):
        cursor = self.request.GET.get("cursor") or None
        data = {
            "categories": Resto.CATEGORIES,
            "restos": Resto.find(cursor=cursor, limit=20),
        }
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class ViewRestosByCategory(Action):

    PAGE_URL_NAME = "friday.view_restos_by_category"
    PAGE_TEMPLATE = "restos/view_restos_by_category.html"

    def __init__(self, request, category):
        super(ViewRestosByCategory, self).__init__(request)
        self.category = category

    def get_page(self):
        category_display = None
        for category, display in Resto.CATEGORIES:
            if category == self.category:
                category_display = display
                break
        category_display = category_display or self.category
        cursor = self.request.GET.get("cursor") or None
        restos = Resto.find_by_category(category=self.category, cursor=cursor, limit=20)
        data = {
            "categories": Resto.CATEGORIES,
            "category_display": category_display,
            "restos": restos,
        }
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class ViewRestoTagCloud(Action):

    AJAX_URL_NAME = "friday.view_resto_tag_cloud"
    AJAX_TEMPLATE = "restos/common/resto_tag_cloud.html"

    def get_ajax(self):
        return {"tag_cloud": Tag.get_cloud(Resto)}


class ViewRestosByTag(Action):

    PAGE_URL_NAME = "friday.view_restos_by_tag"
    PAGE_TEMPLATE = "restos/view_restos_by_tag.html"

    def get_page(self):
        tag_name = self.request.GET.get("tag_name")
        cursor = self.request.GET.get("cursor") or None
        restos = Resto.find_by_tag(name=tag_name, cursor=cursor, limit=20)
        data = {"tag_name": tag_name, "restos": restos}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class CreateResto(Action):

    PAGE_URL_NAME = "friday.create_resto"
    PAGE_TEMPLATE = "restos/create_resto.html"

    def _check_create_access(self):
        if not self.current_user:
            message = "Current user cannot create resto."
            logging.error(message)
            raise BadRequestError(self.request, message)

    def get_page(self):
        self._check_create_access()
        data = {"resto_form": RestoForm()}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        self._check_create_access()
        resto_form = RestoForm(data=self.request.POST)
        try:
            resto = resto_form.create(submitter=self.current_user)
            redirect_url = ViewResto.get_page_url(resto_id=resto.id)
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to create resto in datastore: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"resto_form": resto_form, "prompt": Prompt(error=message)}
            data = self.update_data(data)
            return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class BaseRestoAction(Action):

    def __init__(self, request, resto_id):
        super(BaseRestoAction, self).__init__(request)
        self.resto_id = int(resto_id)

    def get_resto(self):
        resto = Resto.get_unique(id=self.resto_id)
        if not resto:
            message = "searched by resto id %s." % self.resto_id
            raise EntityNotFoundError(Resto, message)
        return resto

    def get_resto_access(self):
        return RestoAccess(self.current_user, self.get_resto())

    def update_data(self, data):
        data["resto"] = self.get_resto()
        data["resto_access"] = self.get_resto_access()
        return super(BaseRestoAction, self).update_data(data)


class ViewResto(BaseRestoAction):

    PAGE_URL_NAME = "friday.view_resto"
    PAGE_TEMPLATE = "restos/view_resto.html"

    def get_page(self):
        data = self.update_data({})
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class ViewRestoTags(BaseRestoAction):

    AJAX_URL_NAME = "friday.view_resto_tags"
    AJAX_TEMPLATE = "restos/common/resto_tags.html"

    def get_ajax(self):
        if self.get_resto_access().can_edit():
            return {"resto_tag_form": RestoTagForm()}
        else:
            return {}

    def post_ajax(self):
        if not self.get_resto_access().can_edit():
            message = "Current user cannot add tags to resto."
            raise BadRequestError(self.request, message)
        resto_tag_form = RestoTagForm(data=self.request.POST)
        try:
            resto_tag_form.add_tags(resto=self.get_resto())
            return {"resto_tag_form": RestoTagForm()}
        except Exception, exc:
            message = "Failed to add tags to resto: %s" % exc
            logging.error(message)
            logging.exception(exc)
            return {"ajax_prompt": Prompt(error=message), "resto_tag_form": resto_tag_form}


class RemoveRestoTag(BaseRestoAction):

    AJAX_URL_NAME = "friday.remove_resto_tag"
    AJAX_TEMPLATE = "restos/common/resto_tag_removed.html"

    def post_ajax(self):
        if not self.get_resto_access().can_edit():
            message = "Current user cannot add tags to resto"
            raise BadRequestError(self.request, message)
        resto = self.get_resto()
        name = self.request.POST.get("name")
        try:
            resto.remove_tags(name)
            resto.save()
            return {"name": name}
        except Exception, exc:
            message = "Failed to remove tag from resto: %s" % exc
            logging.error(message)
            logging.exception(exc)
            return {"ajax_prompt": Prompt(error=message), "name": name}


class EditResto(BaseRestoAction):

    PAGE_URL_NAME = "friday.edit_resto"
    PAGE_TEMPLATE = "restos/edit_resto.html"

    def _check_edit_access(self):
        if not self.get_resto_access().can_edit():
            message = "Current user cannot edit resto %s." % self.get_resto().id
            logging.error(message)
            raise BadRequestError(self.request, message)

    def get_page(self):
        self._check_edit_access()
        resto_form = RestoForm(instance=self.get_resto())
        data = {"resto_form": resto_form}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        self._check_edit_access()
        resto_form = RestoForm(data=self.request.POST, instance=self.get_resto())
        try:
            resto = resto_form.update(updater=self.current_user)
            message = "Resto %s has been updated successfully." % resto.id
            logging.info(message)
            redirect_url = ViewResto.get_page_url(resto_id=resto.id)
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to update resto in datastore: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"resto_form": resto_form, "prompt": Prompt(error=message)}
            data = self.update_data(data)
            return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class DeleteResto(BaseRestoAction):

    PAGE_URL_NAME = "friday.delete_resto"
    PAGE_TEMPLATE = "restos/delete_resto.html"

    def _check_delete_access(self):
        if not self.get_resto_access().can_delete():
            message = "Current user cannot delete resto %s." % self.get_resto().id
            logging.error(message)
            raise BadRequestError(self.request, message)

    def get_page(self):
        self._check_delete_access()
        data = self.update_data({})
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        self._check_delete_access()
        try:
            resto = self.get_resto()
            resto_id = resto.id  # Resto instance has no 'id' attribute after deletion.
            resto.delete()
            message = "Resto %s has been deleted successfully." % resto_id
            logging.info(message)
            redirect_url = ViewAllRestos.get_page_url()
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to delete resto in datastore: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"prompt": Prompt(error=message)}
            data = self.update_data(data)
            return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class ChangeRestoFave(BaseRestoAction):

    AJAX_URL_NAME = "friday.change_resto_fave"
    AJAX_TEMPLATE = "restos/common/resto_faves.html"

    def post_ajax(self):
        if not self.current_user:
            message = "Anonymous user cannot add/remove a resto to/from faves."
            raise BadRequestError(self.request, message)
        resto = self.get_resto()
        resto.change_fave(self.current_user)
        return {}


class RecommendDish(BaseRestoAction):

    PAGE_URL_NAME = "friday.recommend_dish"
    PAGE_TEMPLATE = "restos/recommend_dish.html"

    def _check_create_access(self):
        if not self.get_resto_access().can_edit():
            message = "Current user cannot recommend dish of resto %s." % self.get_resto().id
            logging.error(message)
            raise BadRequestError(self.request, message)

    def get_page(self):
        self._check_create_access()
        dish_form = DishForm()
        data = {"dish_form": dish_form}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        self._check_create_access()
        dish_form = DishForm(data=self.request.POST)
        try:
            dish = dish_form.create(resto=self.get_resto())
            message = "Dish %s has been created successfully." % dish.id
            logging.info(message)
            redirect_url = ViewResto.get_page_url(resto_id=dish.resto.id)
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to create dish in datastore: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"dish_form": dish_form, "prompt": Prompt(error=message)}
            data = self.update_data(data)
            return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class BaseDishAction(BaseRestoAction):

    def __init__(self, request, resto_id, dish_id):
        super(BaseDishAction, self).__init__(request, resto_id)
        self.dish_id = int(dish_id)

    def get_dish(self):
        dish = Dish.get_unique(id=self.dish_id)
        if not dish or dish.resto != self.get_resto():
            message = "searched by dish id %s." % self.dish_id
            raise EntityNotFoundError(Dish, message)
        return dish

    def update_data(self, data):
        data["dish"] = self.get_dish()
        return super(BaseDishAction, self).update_data(data)


class ChangeDishFan(BaseDishAction):

    AJAX_URL_NAME = "friday.change_dish_fan"
    AJAX_TEMPLATE = "restos/common/dish.html"

    def post_ajax(self):
        if not self.current_user:
            message = "Anonymous user cannot like/unlike a dish."
            raise BadRequestError(self.request, message)
        dish = self.get_dish()
        dish.change_fan(self.current_user)
        return {}


class EditDish(BaseDishAction):

    PAGE_URL_NAME = "friday.edit_dish"
    PAGE_TEMPLATE = "restos/edit_dish.html"

    def _check_edit_access(self):
        if not self.get_resto_access().can_edit():
            message = "Current user cannot edit dish of resto %s." % self.get_resto().id
            logging.error(message)
            raise BadRequestError(self.request, message)

    def get_page(self):
        self._check_edit_access()
        dish_form = DishForm(instance=self.get_dish())
        data = {"dish_form": dish_form}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        self._check_edit_access()
        dish_form = DishForm(data=self.request.POST, instance=self.get_dish())
        try:
            dish = dish_form.update()
            message = "Dish %s has been updated successfully." % dish.id
            logging.info(message)
            redirect_url = ViewResto.get_page_url(resto_id=dish.resto.id)
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to update dish in datastore: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"dish_form": dish_form, "prompt": Prompt(error=message)}
            data = self.update_data(data)
            return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class DeleteDish(BaseDishAction):

    PAGE_URL_NAME = "friday.delete_dish"
    PAGE_TEMPLATE = "restos/delete_dish.html"

    def _check_delete_access(self):
        if not self.get_resto_access().can_edit():
            message = "Current user cannot delete dish %s." % self.get_dish().id
            logging.error(message)
            raise BadRequestError(self.request, message)

    def get_page(self):
        self._check_delete_access()
        data = self.update_data({})
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))

    def post_page(self):
        self._check_delete_access()
        try:
            dish = self.get_dish()
            dish_id = dish.id  # Dish instance has no 'id' attribute after deletion.
            dish.delete()
            message = "Dish %s has been deleted successfully." % dish_id
            logging.info(message)
            redirect_url = ViewResto.get_page_url(resto_id=self.get_resto().id)
            return HttpResponseRedirect(redirect_url)
        except Exception, exc:
            message = "Failed to delete dish in datastore: %s" % exc
            logging.error(message)
            logging.exception(exc)
            data = {"prompt": Prompt(error=message)}
            data = self.update_data(data)
            return render_to_response(self.get_page_template(), data, RequestContext(self.request))


class SearchDish(Action):

    PAGE_URL_NAME = "friday.search_dish"
    PAGE_TEMPLATE = "restos/search_dish.html"

    def get_page(self):
        dish_name = self.request.GET.get("dish_name")
        data = {"dish_name": dish_name, "dishes": Dish.find_by_name(dish_name)}
        data = self.update_data(data)
        return render_to_response(self.get_page_template(), data, RequestContext(self.request))


#---------------------------------------------------------------------------------------------------


def restos_home(request):
    return RestosHome(request).process()


def view_all_restos(request):
    return ViewAllRestos(request).process()


def view_restos_by_category(request, category):
    return ViewRestosByCategory(request, category).process()


def view_resto_tag_cloud(request):
    return ViewRestoTagCloud(request).process()


def view_restos_by_tag(request):
    return ViewRestosByTag(request).process()


def create_resto(request):
    return CreateResto(request).process()


def view_resto(request, resto_id):
    return ViewResto(request, resto_id).process()


def view_resto_tags(request, resto_id):
    return ViewRestoTags(request, resto_id).process()


def remove_resto_tag(request, resto_id):
    return RemoveRestoTag(request, resto_id).process()


def edit_resto(request, resto_id):
    return EditResto(request, resto_id).process()


def delete_resto(request, resto_id):
    return DeleteResto(request, resto_id).process()


def change_resto_fave(request, resto_id):
    return ChangeRestoFave(request, resto_id).process()


def recommend_dish(request, resto_id):
    return RecommendDish(request, resto_id).process()


def change_dish_fan(request, resto_id, dish_id):
    return ChangeDishFan(request, resto_id, dish_id).process()


def edit_dish(request, resto_id, dish_id):
    return EditDish(request, resto_id, dish_id).process()


def delete_dish(request, resto_id, dish_id):
    return DeleteDish(request, resto_id, dish_id).process()


def search_dish(request):
    return SearchDish(request).process()


# EOF
