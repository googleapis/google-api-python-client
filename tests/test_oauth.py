#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc.
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


"""Oauth tests

Unit tests for apiclient.oauth.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

# Do not remove the httplib2 import
import httplib2
import unittest

from apiclient.http import HttpMockSequence
from apiclient.oauth import CredentialsInvalidError
from apiclient.oauth import MissingParameter
from apiclient.oauth import TwoLeggedOAuthCredentials


class TwoLeggedOAuthCredentialsTests(unittest.TestCase):

  def setUp(self):
    client_id = "some_client_id"
    client_secret = "cOuDdkfjxxnv+"
    user_agent = "sample/1.0"
    self.credentials = TwoLeggedOAuthCredentials(client_id, client_secret,
        user_agent)
    self.credentials.requestor = 'test@example.org'

  def test_invalid_token(self):
    http = HttpMockSequence([
      ({'status': '401'}, ''),
      ])
    http = self.credentials.authorize(http)
    try:
      resp, content = http.request("http://example.com")
      self.fail('should raise CredentialsInvalidError')
    except CredentialsInvalidError:
      pass

  def test_no_requestor(self):
    self.credentials.requestor = None
    http = HttpMockSequence([
      ({'status': '401'}, ''),
      ])
    http = self.credentials.authorize(http)
    try:
      resp, content = http.request("http://example.com")
      self.fail('should raise MissingParameter')
    except MissingParameter:
      pass

  def test_add_requestor_to_uri(self):
    http = HttpMockSequence([
      ({'status': '200'}, 'echo_request_uri'),
      ])
    http = self.credentials.authorize(http)
    resp, content = http.request("http://example.com")
    self.assertEqual('http://example.com?xoauth_requestor_id=test%40example.org',
                     content)

if __name__ == '__main__':
  unittest.main()
