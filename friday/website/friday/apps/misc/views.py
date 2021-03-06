#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-02-08.
# $Id$
#

import datetime
import urllib

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

from friday.auth import users
from friday.common.errors import ProgrammingError


class Splash(object):

    def __init__(self, isoweekday):
        super(Splash, self).__init__()
        self.isoweekday = int(isoweekday)
        if self.isoweekday == 1:
            self.weekday_name = "Monday"
            self.image = "the_persistence_of_memory.jpg"
            self.title = "The Persistence of Memory (1931)"
            self.artist = "Salvador Dali"
        elif self.isoweekday == 2:
            self.weekday_name = "Tuesday"
            self.image = "the_scream.jpg"
            self.title = "The Scream (1893)"
            self.artist = "Edvard Munch"
        elif self.isoweekday == 3:
            self.weekday_name = "Wednesday"
            self.image = "barge_haulers_on_the_volga.jpg"
            self.title = "Barge Haulers on the Volga (1870-1873)"
            self.artist = "Ilya Repin"
        elif self.isoweekday == 4:
            self.weekday_name = "Thursday"
            self.image = "the_raft_of_the_medusa.jpg"
            self.title = "The Raft of the Medusa (1819)"
            self.artist = "Théodore Géricault"
        elif self.isoweekday == 5:
            self.weekday_name = "Friday"
            self.image = "liberty_leading_the_people.jpg"
            self.title = "Liberty Leading the People (1830)"
            self.artist = "Eugène Delacroix"
        elif self.isoweekday == 6:
            self.weekday_name = "Saturday"
            self.image = "le_moulin_de_la_galette.jpg"
            self.title = "Le moulin de la Galette (1876)"
            self.artist = "Pierre-Auguste Renoir"
        elif self.isoweekday == 7:
            self.weekday_name = "Sunday"
            self.image = "sunday_afternoon_on_the_island_of_la_grande_jatte.jpg"
            self.title = "Sunday Afternoon on the Island of La Grande Jatte (1884-1886)"
            self.artist = "Georges Seurat"
        else:
            message = "Invalid ISO weekday %s." % isoweekday
            raise ProgrammingError(message)

    @property
    def countdown(self):
        return max(0, 5 - self.isoweekday)

    @property
    def is_friday(self):
        return self.isoweekday == 5

    @property
    def is_weekend(self):
        return self.isoweekday in (6, 7)

    @property
    def artist_url(self):
        return "http://en.wikipedia.org/wiki/%s" % urllib.quote(self.artist.replace(" ", "_"))


def welcome(request):
    current_user = users.get_current_user(request)
    if current_user:
        redirect_url = reverse("friday.home")
        return HttpResponseRedirect(redirect_url)
    splash = None
    if request.REQUEST.get("isoweekday"):
        try:
            splash = Splash(request.REQUEST.get("isoweekday"))
        except ValueError:
            splash = None
    splash = splash or Splash(datetime.date.today().isoweekday())
    data = {"splash": splash}
    return render_to_response("misc/welcome.html", data, RequestContext(request))


def home(request):
    # TODO: as we have only one group at this moment, we redirect to the group page.
    redirect_url = reverse("friday.view_group", kwargs={"group_uid": "vivelevendredi"})
    return HttpResponseRedirect(redirect_url)
    #data = {}
    #return render_to_response("misc/home.html", data, RequestContext(request))


def about(request, topic=None):
    _TOPICS = ("browser", "versions")
    if topic not in _TOPICS:
        template_file = "misc/about.html"
    else:
        template_file = "misc/about_%s.html" % topic
    data = {}
    return render_to_response(template_file, data, RequestContext(request))


def not_found(request):
    data = {"bad_url": request.path}
    response = render_to_response("misc/not_found.html", data, RequestContext(request))
    response.status_code = 404  # not found.
    return response


# EOF
