#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 ZHENG Zhong <http://www.zhengzhong.net/>
#
# Created on 2010-04-27.
# $Id$
#

import types

from google.appengine.ext import db
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from djangomockup.models.manager import Manager
from djangomockup.models.signals import pre_save, post_save, pre_delete, post_delete


class ModelMetaclass(db.PropertiedClass):
    """
    Metaclass for the combined Django + App Engine model class.

    This metaclass inherits from db.PropertiedClass in the Google App Engine library.
    This metaclass has two additional purposes:

    - Register each model class created with Django (the parent class will take care of registering
      it with the appengine libraries).
    - Add the (minimum number) of attributes and methods to make Django believe the class is a
      normal Django model.

    The resulting classes are still not generally useful as Django classes and are intended to be
    used by Django only in limited situations such as loading and dumping fixtures.
    """

    def __new__(cls, name, bases, attrs):
        if name == "Model":
            # This metaclass only acts on sub-classes of Model.
            return super(ModelMetaclass, cls).__new__(cls, name, bases, attrs)
        new_class = super(ModelMetaclass, cls).__new__(cls, name, bases, attrs)
        #new_class._meta = ModelOptions(new_class)
        new_class.objects = Manager(new_class)
        new_class._default_manager = new_class.objects
        new_class.DoesNotExist = types.ClassType("DoesNotExist", (ObjectDoesNotExist,), {})
        return new_class


class Model(db.Model):
    """
    This class simulates some of the Django Model class' behaviors, including:
    - provide a 'pk' property, which is the primary key (id or key_name) of the instance.
    - provide an 'id' property if the instance's key has an id.
    - provide a class attribute 'objects', which is the model manager.
    - send signals on saving/deleting an instance.

    All model classes should derive from this class.
    """

    __metaclass__ = ModelMetaclass

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return unicode(self.key()) == unicode(other.key())

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def pk(self):
        if self.is_saved():
            return self.key().id() or self.key().name()
        else:
            raise AttributeError("%s object has no attribute 'pk'" % self.__class__.__name__)

    @property
    def id(self):
        if self.is_saved() and self.key().id():
            return self.key().id()
        else:
            raise AttributeError("%s object has no attribute 'id'" % self.__class__.__name__)

    def save(self):
        pre_save.send(sender=self.__class__, instance=self)
        created = not self.is_saved()
        super(Model, self).put()
        post_save.send(sender=self.__class__, instance=self, created=created)

    def delete(self):
        pre_delete.send(sender=self.__class__, instance=self)
        super(Model, self).delete()
        post_delete.send(sender=self.__class__, instance=self)

    @classmethod
    def delete_all(cls):
        all_instances = cls.all()
        deleted = 0
        for instance in all_instances:
            instance.delete()
            deleted += 1
        return deleted


# EOF
