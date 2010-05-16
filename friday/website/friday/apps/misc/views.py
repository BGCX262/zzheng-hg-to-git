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
            self.slogan = "Monday"
            self.image = "the_scream.jpg"
            self.title = "The Scream (1893)"
            self.artist = "Edvard Munch"
        elif self.isoweekday == 2:
            self.weekday_name = "Tuesday"
            self.slogan = "Tuesday"
            self.image = "christ_in_the_desert.jpg"
            self.title = "Christ in the Desert (1872)"
            self.artist = "Ivan Kramskoi"
        elif self.isoweekday == 3:
            self.weekday_name = "Wednesday"
            self.slogan = "Wednesday"
            self.image = ""
            self.title = ""
            self.artist = ""
        elif self.isoweekday == 4:
            self.weekday_name = "Thursday"
            self.slogan = "Thursday"
            self.image = "the_raft_of_the_medusa.jpg"
            self.title = "The Raft of the Medusa (1819)"
            self.artist = "Théodore Géricault"
        elif self.isoweekday == 5:
            self.weekday_name = "Friday"
            self.slogan = "Friday"
            self.image = "liberty_leading_the_people.jpg"
            self.title = "Liberty Leading the People (1830)"
            self.artist = "Eugène Delacroix"
        elif self.isoweekday == 6:
            self.weekday_name = "Saturday"
            self.slogan = "Saturday"
            self.image = "le_moulin_de_la_galette.jpg"
            self.title = "Le moulin de la Galette (1876)"
            self.artist = "Pierre-Auguste Renoir"
        elif self.isoweekday == 7:
            self.weekday_name = "Sunday"
            self.slogan = "Sunday"
            self.image = ""
            self.title = ""
            self.artist = ""
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
    data = {}
    return render_to_response("misc/home.html", data, RequestContext(request))


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
    return render_to_response("misc/not_found.html", data, RequestContext(request))


# EOF
