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


"""Oauth2client tests

Unit tests for oauth2client.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import httplib2
import unittest
import urlparse

try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

from apiclient.http import HttpMockSequence
from oauth2client.client import AccessTokenCredentials
from oauth2client.client import AccessTokenCredentialsError
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import AssertionCredentials
from oauth2client.client import FlowExchangeError
from oauth2client.client import OAuth2Credentials
from oauth2client.client import OAuth2WebServerFlow


class OAuth2CredentialsTests(unittest.TestCase):

  def setUp(self):
    access_token = "foo"
    client_id = "some_client_id"
    client_secret = "cOuDdkfjxxnv+"
    refresh_token = "1/0/a.df219fjls0"
    token_expiry = "ignored"
    token_uri = "https://www.google.com/accounts/o8/oauth2/token"
    user_agent = "refresh_checker/1.0"
    self.credentials = OAuth2Credentials(
      access_token, client_id, client_secret,
      refresh_token, token_expiry, token_uri,
      user_agent)

  def test_token_refresh_success(self):
    http = HttpMockSequence([
      ({'status': '401'}, ''),
      ({'status': '200'}, '{"access_token":"1/3w","expires_in":3600}'),
      ({'status': '200'}, 'echo_request_headers'),
      ])
    http = self.credentials.authorize(http)
    resp, content = http.request("http://example.com")
    self.assertEqual(content['authorization'], 'OAuth 1/3w')

  def test_token_refresh_failure(self):
    http = HttpMockSequence([
      ({'status': '401'}, ''),
      ({'status': '400'}, '{"error":"access_denied"}'),
      ])
    http = self.credentials.authorize(http)
    try:
      http.request("http://example.com")
      self.fail("should raise AccessTokenRefreshError exception")
    except AccessTokenRefreshError:
      pass

  def test_non_401_error_response(self):
    http = HttpMockSequence([
      ({'status': '400'}, ''),
      ])
    http = self.credentials.authorize(http)
    resp, content = http.request("http://example.com")
    self.assertEqual(400, resp.status)


class AccessTokenCredentialsTests(unittest.TestCase):

  def setUp(self):
    access_token = "foo"
    user_agent = "refresh_checker/1.0"
    self.credentials = AccessTokenCredentials(access_token, user_agent)

  def test_token_refresh_success(self):
    http = HttpMockSequence([
      ({'status': '401'}, ''),
      ])
    http = self.credentials.authorize(http)
    try:
      resp, content = http.request("http://example.com")
      self.fail("should throw exception if token expires")
    except AccessTokenCredentialsError:
      pass
    except Exception:
      self.fail("should only throw AccessTokenCredentialsError")

  def test_non_401_error_response(self):
    http = HttpMockSequence([
      ({'status': '400'}, ''),
      ])
    http = self.credentials.authorize(http)
    resp, content = http.request('http://example.com')
    self.assertEqual(400, resp.status)

  def test_auth_header_sent(self):
    http = HttpMockSequence([
      ({'status': '200'}, 'echo_request_headers'),
      ])
    http = self.credentials.authorize(http)
    resp, content = http.request('http://example.com')
    self.assertEqual(content['authorization'], 'OAuth foo')

class TestAssertionCredentials(unittest.TestCase):
  assertion_text = "This is the assertion"
  assertion_type = "http://www.google.com/assertionType"

  class AssertionCredentialsTestImpl(AssertionCredentials):

    def _generate_assertion(self):
      return TestAssertionCredentials.assertion_text

  def setUp(self):
    user_agent = "fun/2.0"
    self.credentials = self.AssertionCredentialsTestImpl(self.assertion_type,
        user_agent)

  def test_assertion_body(self):
    body = urlparse.parse_qs(self.credentials._generate_refresh_request_body())
    self.assertEqual(body['assertion'][0], self.assertion_text)
    self.assertEqual(body['assertion_type'][0], self.assertion_type)

  def test_assertion_refresh(self):
    http = HttpMockSequence([
      ({'status': '200'}, '{"access_token":"1/3w"}'),
      ({'status': '200'}, 'echo_request_headers'),
      ])
    http = self.credentials.authorize(http)
    resp, content = http.request("http://example.com")
    self.assertEqual(content['authorization'], 'OAuth 1/3w')


class OAuth2WebServerFlowTest(unittest.TestCase):

  def setUp(self):
    self.flow = OAuth2WebServerFlow(
        client_id='client_id+1',
        client_secret='secret+1',
        scope='foo',
        user_agent='unittest-sample/1.0',
        )

  def test_construct_authorize_url(self):
    authorize_url = self.flow.step1_get_authorize_url('oob')

    parsed = urlparse.urlparse(authorize_url)
    q = parse_qs(parsed[4])
    self.assertEqual(q['client_id'][0], 'client_id+1')
    self.assertEqual(q['response_type'][0], 'code')
    self.assertEqual(q['scope'][0], 'foo')
    self.assertEqual(q['redirect_uri'][0], 'oob')

  def test_exchange_failure(self):
    http = HttpMockSequence([
      ({'status': '400'}, '{"error":"invalid_request"}'),
      ])

    try:
      credentials = self.flow.step2_exchange('some random code', http)
      self.fail("should raise exception if exchange doesn't get 200")
    except FlowExchangeError:
      pass

  def test_exchange_success(self):
    http = HttpMockSequence([
      ({'status': '200'},
      """{ "access_token":"SlAV32hkKG",
       "expires_in":3600,
       "refresh_token":"8xLOxBtZp8" }"""),
      ])

    credentials = self.flow.step2_exchange('some random code', http)
    self.assertEqual(credentials.access_token, 'SlAV32hkKG')
    self.assertNotEqual(credentials.token_expiry, None)
    self.assertEqual(credentials.refresh_token, '8xLOxBtZp8')

  def test_exchange_no_expires_in(self):
    http = HttpMockSequence([
      ({'status': '200'}, """{ "access_token":"SlAV32hkKG",
       "refresh_token":"8xLOxBtZp8" }"""),
      ])

    credentials = self.flow.step2_exchange('some random code', http)
    self.assertEqual(credentials.token_expiry, None)


if __name__ == '__main__':
  unittest.main()
