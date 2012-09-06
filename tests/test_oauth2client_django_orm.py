#!/usr/bin/python2.4
#
# Copyright 2011 Google Inc.
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


"""Discovery document tests

Unit tests for objects created from discovery documents.
"""

__author__ = 'conleyo@google.com (Conley Owens)'

import base64
import imp
import os
import pickle
import sys
import unittest

# Ensure that if app engine is available, we use the correct django from it
try:
  from google.appengine.dist import use_library
  use_library('django', '1.2')
except ImportError:
  pass

from oauth2client.client import Credentials
from oauth2client.client import Flow

# Mock a Django environment
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_settings'
sys.modules['django_settings'] = imp.new_module('django_settings')

from oauth2client.django_orm import CredentialsField
from oauth2client.django_orm import FlowField


class TestCredentialsField(unittest.TestCase):
  def setUp(self):
    self.field = CredentialsField()
    self.credentials = Credentials()
    self.pickle = base64.b64encode(pickle.dumps(self.credentials))

  def test_field_is_text(self):
    self.assertEquals(self.field.get_internal_type(), 'TextField')

  def test_field_unpickled(self):
    self.assertTrue(isinstance(self.field.to_python(self.pickle), Credentials))

  def test_field_pickled(self):
    prep_value = self.field.get_db_prep_value(self.credentials,
                                              connection=None)
    self.assertEqual(prep_value, self.pickle)


class TestFlowField(unittest.TestCase):
  def setUp(self):
    self.field = FlowField()
    self.flow = Flow()
    self.pickle = base64.b64encode(pickle.dumps(self.flow))

  def test_field_is_text(self):
    self.assertEquals(self.field.get_internal_type(), 'TextField')

  def test_field_unpickled(self):
    self.assertTrue(isinstance(self.field.to_python(self.pickle), Flow))

  def test_field_pickled(self):
    prep_value = self.field.get_db_prep_value(self.flow, connection=None)
    self.assertEqual(prep_value, self.pickle)


if __name__ == '__main__':
  unittest.main()
