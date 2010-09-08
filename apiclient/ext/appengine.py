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

Utilities for making it easier to use the
Google API Client for Python on Google App Engine.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import pickle

from google.appengine.ext import db
from apiclient.oauth import OAuthCredentials
from apiclient.oauth import FlowThreeLegged


class FlowThreeLeggedProperty(db.Property):
  """Utility property that allows easy
  storage and retreival of an
  apiclient.oauth.FlowThreeLegged"""

  # Tell what the user type is.
  data_type = FlowThreeLegged

  # For writing to datastore.
  def get_value_for_datastore(self, model_instance):
    flow = super(FlowThreeLeggedProperty,
                 self).get_value_for_datastore(model_instance)
    return db.Blob(pickle.dumps(flow))

  # For reading from datastore.
  def make_value_from_datastore(self, value):
    if value is None:
      return None
    return pickle.loads(value)

  def validate(self, value):
    if value is not None and not isinstance(value, FlowThreeLegged):
      raise BadValueError('Property %s must be convertible '
                          'to a FlowThreeLegged instance (%s)' %
                          (self.name, value))
    return super(FlowThreeLeggedProperty, self).validate(value)

  def empty(self, value):
    return not value


class OAuthCredentialsProperty(db.Property):
  """Utility property that allows easy
  storage and retrieval of
  apiclient.oath.OAuthCredentials
  """

  # Tell what the user type is.
  data_type = OAuthCredentials

  # For writing to datastore.
  def get_value_for_datastore(self, model_instance):
    cred = super(OAuthCredentialsProperty,
                 self).get_value_for_datastore(model_instance)
    return db.Blob(pickle.dumps(cred))

  # For reading from datastore.
  def make_value_from_datastore(self, value):
    if value is None:
      return None
    return pickle.loads(value)

  def validate(self, value):
    if value is not None and not isinstance(value, OAuthCredentials):
      raise BadValueError('Property %s must be convertible '
                          'to an OAuthCredentials instance (%s)' %
                          (self.name, value))
    return super(OAuthCredentialsProperty, self).validate(value)

  def empty(self, value):
    return not value
