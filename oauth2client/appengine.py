# Copyright (C) 2010 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utilities for Google App Engine

Utilities for making it easier to use OAuth 2.0 on Google App Engine.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import pickle

from google.appengine.ext import db
from client import Credentials
from client import Flow
from client import Storage


class FlowProperty(db.Property):
  """App Engine datastore Property for Flow.

  Utility property that allows easy storage and retreival of an
  oauth2client.Flow"""

  # Tell what the user type is.
  data_type = Flow

  # For writing to datastore.
  def get_value_for_datastore(self, model_instance):
    flow = super(FlowProperty,
                 self).get_value_for_datastore(model_instance)
    return db.Blob(pickle.dumps(flow))

  # For reading from datastore.
  def make_value_from_datastore(self, value):
    if value is None:
      return None
    return pickle.loads(value)

  def validate(self, value):
    if value is not None and not isinstance(value, Flow):
      raise BadValueError('Property %s must be convertible '
                          'to a FlowThreeLegged instance (%s)' %
                          (self.name, value))
    return super(FlowProperty, self).validate(value)

  def empty(self, value):
    return not value


class CredentialsProperty(db.Property):
  """App Engine datastore Property for Credentials.

  Utility property that allows easy storage and retrieval of
  oath2client.Credentials
  """

  # Tell what the user type is.
  data_type = Credentials

  # For writing to datastore.
  def get_value_for_datastore(self, model_instance):
    cred = super(CredentialsProperty,
                 self).get_value_for_datastore(model_instance)
    return db.Blob(pickle.dumps(cred))

  # For reading from datastore.
  def make_value_from_datastore(self, value):
    if value is None:
      return None
    return pickle.loads(value)

  def validate(self, value):
    if value is not None and not isinstance(value, Credentials):
      raise BadValueError('Property %s must be convertible '
                          'to an Credentials instance (%s)' %
                          (self.name, value))
    return super(CredentialsProperty, self).validate(value)

  def empty(self, value):
    return not value


class StorageByKeyName(Storage):
  """Store and retrieve a single credential to and from
  the App Engine datastore.

  This Storage helper presumes the Credentials
  have been stored as a CredenialsProperty
  on a datastore model class, and that entities
  are stored by key_name.
  """

  def __init__(self, model, key_name, property_name):
    """Constructor for Storage.

    Args:
      model: db.Model, model class
      key_name: string, key name for the entity that has the credentials
      property_name: string, name of the property that is an CredentialsProperty
    """
    self._model = model
    self._key_name = key_name
    self._property_name = property_name

  def get(self):
    """Retrieve Credential from datastore.

    Returns:
      oauth2client.Credentials
    """
    entity = self._model.get_or_insert(self._key_name)
    credential = getattr(entity, self._property_name)
    if credential and hasattr(credential, 'set_store'):
      credential.set_store(self.put)
    return credential

  def put(self, credentials):
    """Write a Credentials to the datastore.

    Args:
      credentials: Credentials, the credentials to store.
    """
    entity = self._model.get_or_insert(self._key_name)
    setattr(entity, self._property_name, credentials)
    entity.put()
