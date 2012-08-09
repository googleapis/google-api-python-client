# Copyright 2012 Google Inc.
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


"""Tests for oauth2client.gce.

Unit tests for oauth2client.gce.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import unittest
import mox

from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import Credentials
from oauth2client.gce import AppAssertionCredentials


class AssertionCredentialsTests(unittest.TestCase):

  def test_good_refresh(self):
    m = mox.Mox()

    httplib2_response = m.CreateMock(object)
    httplib2_response.status = 200

    httplib2_request = m.CreateMock(object)
    httplib2_request.__call__(
        ('http://metadata.google.internal/0.1/meta-data/service-accounts/'
         'default/acquire'
         '?scope=http%3A%2F%2Fexample.com%2Fa%20http%3A%2F%2Fexample.com%2Fb'
        )).AndReturn((httplib2_response, '{"accessToken": "this-is-a-token"}'))

    m.ReplayAll()

    c = AppAssertionCredentials(scope=['http://example.com/a',
                                       'http://example.com/b'])

    c._refresh(httplib2_request)

    self.assertEquals('this-is-a-token', c.access_token)

    m.UnsetStubs()
    m.VerifyAll()


  def test_fail_refresh(self):
    m = mox.Mox()

    httplib2_response = m.CreateMock(object)
    httplib2_response.status = 400

    httplib2_request = m.CreateMock(object)
    httplib2_request.__call__(
        ('http://metadata.google.internal/0.1/meta-data/service-accounts/'
         'default/acquire'
         '?scope=http%3A%2F%2Fexample.com%2Fa%20http%3A%2F%2Fexample.com%2Fb'
        )).AndReturn((httplib2_response, '{"accessToken": "this-is-a-token"}'))

    m.ReplayAll()

    c = AppAssertionCredentials(scope=['http://example.com/a',
                                       'http://example.com/b'])

    try:
      c._refresh(httplib2_request)
      self.fail('Should have raised exception on 400')
    except AccessTokenRefreshError:
      pass

    m.UnsetStubs()
    m.VerifyAll()

  def test_to_from_json(self):
    c = AppAssertionCredentials(scope=['http://example.com/a',
                                       'http://example.com/b'])
    json = c.to_json()
    c2 = Credentials.new_from_json(json)

    self.assertEqual(c.access_token, c2.access_token)
