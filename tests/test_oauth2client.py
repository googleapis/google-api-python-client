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

import base64
import datetime
import httplib2
import os
import unittest
import urlparse

try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

from apiclient.http import HttpMockSequence
from oauth2client.anyjson import simplejson
from oauth2client.client import AccessTokenCredentials
from oauth2client.client import AccessTokenCredentialsError
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import AssertionCredentials
from oauth2client.client import Credentials
from oauth2client.client import FlowExchangeError
from oauth2client.client import MemoryCache
from oauth2client.client import OAuth2Credentials
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import OOB_CALLBACK_URN
from oauth2client.client import VerifyJwtTokenError
from oauth2client.client import _extract_id_token
from oauth2client.client import credentials_from_code
from oauth2client.client import credentials_from_clientsecrets_and_code

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def datafile(filename):
  return os.path.join(DATA_DIR, filename)


class CredentialsTests(unittest.TestCase):

  def test_to_from_json(self):
    credentials = Credentials()
    json = credentials.to_json()
    restored = Credentials.new_from_json(json)


class OAuth2CredentialsTests(unittest.TestCase):

  def setUp(self):
    access_token = "foo"
    client_id = "some_client_id"
    client_secret = "cOuDdkfjxxnv+"
    refresh_token = "1/0/a.df219fjls0"
    token_expiry = datetime.datetime.utcnow()
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
    self.assertEqual('Bearer 1/3w', content['Authorization'])
    self.assertFalse(self.credentials.access_token_expired)

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
    self.assertTrue(self.credentials.access_token_expired)

  def test_non_401_error_response(self):
    http = HttpMockSequence([
      ({'status': '400'}, ''),
      ])
    http = self.credentials.authorize(http)
    resp, content = http.request("http://example.com")
    self.assertEqual(400, resp.status)

  def test_to_from_json(self):
    json = self.credentials.to_json()
    instance = OAuth2Credentials.from_json(json)
    self.assertEqual(OAuth2Credentials, type(instance))
    instance.token_expiry = None
    self.credentials.token_expiry = None

    self.assertEqual(instance.__dict__, self.credentials.__dict__)


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
    self.assertEqual('Bearer foo', content['Authorization'])


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
    self.assertEqual(self.assertion_text, body['assertion'][0])
    self.assertEqual(self.assertion_type, body['assertion_type'][0])

  def test_assertion_refresh(self):
    http = HttpMockSequence([
      ({'status': '200'}, '{"access_token":"1/3w"}'),
      ({'status': '200'}, 'echo_request_headers'),
      ])
    http = self.credentials.authorize(http)
    resp, content = http.request("http://example.com")
    self.assertEqual('Bearer 1/3w', content['Authorization'])


class ExtractIdTokenText(unittest.TestCase):
  """Tests _extract_id_token()."""

  def test_extract_success(self):
    body = {'foo': 'bar'}
    payload = base64.urlsafe_b64encode(simplejson.dumps(body)).strip('=')
    jwt = 'stuff.' + payload + '.signature'

    extracted = _extract_id_token(jwt)
    self.assertEqual(extracted, body)

  def test_extract_failure(self):
    body = {'foo': 'bar'}
    payload = base64.urlsafe_b64encode(simplejson.dumps(body)).strip('=')
    jwt = 'stuff.' + payload

    self.assertRaises(VerifyJwtTokenError, _extract_id_token, jwt)

class OAuth2WebServerFlowTest(unittest.TestCase):

  def setUp(self):
    self.flow = OAuth2WebServerFlow(
        client_id='client_id+1',
        client_secret='secret+1',
        scope='foo',
        user_agent='unittest-sample/1.0',
        )

  def test_construct_authorize_url(self):
    authorize_url = self.flow.step1_get_authorize_url('OOB_CALLBACK_URN')

    parsed = urlparse.urlparse(authorize_url)
    q = parse_qs(parsed[4])
    self.assertEqual('client_id+1', q['client_id'][0])
    self.assertEqual('code', q['response_type'][0])
    self.assertEqual('foo', q['scope'][0])
    self.assertEqual('OOB_CALLBACK_URN', q['redirect_uri'][0])
    self.assertEqual('offline', q['access_type'][0])

  def test_override_flow_access_type(self):
    """Passing access_type overrides the default."""
    flow = OAuth2WebServerFlow(
        client_id='client_id+1',
        client_secret='secret+1',
        scope='foo',
        user_agent='unittest-sample/1.0',
        access_type='online'
        )
    authorize_url = flow.step1_get_authorize_url('OOB_CALLBACK_URN')

    parsed = urlparse.urlparse(authorize_url)
    q = parse_qs(parsed[4])
    self.assertEqual('client_id+1', q['client_id'][0])
    self.assertEqual('code', q['response_type'][0])
    self.assertEqual('foo', q['scope'][0])
    self.assertEqual('OOB_CALLBACK_URN', q['redirect_uri'][0])
    self.assertEqual('online', q['access_type'][0])

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
    self.assertEqual('SlAV32hkKG', credentials.access_token)
    self.assertNotEqual(None, credentials.token_expiry)
    self.assertEqual('8xLOxBtZp8', credentials.refresh_token)

  def test_exchange_no_expires_in(self):
    http = HttpMockSequence([
      ({'status': '200'}, """{ "access_token":"SlAV32hkKG",
       "refresh_token":"8xLOxBtZp8" }"""),
      ])

    credentials = self.flow.step2_exchange('some random code', http)
    self.assertEqual(None, credentials.token_expiry)

  def test_exchange_fails_if_no_code(self):
    http = HttpMockSequence([
      ({'status': '200'}, """{ "access_token":"SlAV32hkKG",
       "refresh_token":"8xLOxBtZp8" }"""),
      ])

    code = {'error': 'thou shall not pass'}
    try:
      credentials = self.flow.step2_exchange(code, http)
      self.fail('should raise exception if no code in dictionary.')
    except FlowExchangeError, e:
      self.assertTrue('shall not pass' in str(e))

  def test_exchange_id_token_fail(self):
    http = HttpMockSequence([
      ({'status': '200'}, """{ "access_token":"SlAV32hkKG",
       "refresh_token":"8xLOxBtZp8",
       "id_token": "stuff.payload"}"""),
      ])

    self.assertRaises(VerifyJwtTokenError, self.flow.step2_exchange,
      'some random code', http)

  def test_exchange_id_token_fail(self):
    body = {'foo': 'bar'}
    payload = base64.urlsafe_b64encode(simplejson.dumps(body)).strip('=')
    jwt = (base64.urlsafe_b64encode('stuff')+ '.' + payload + '.' +
           base64.urlsafe_b64encode('signature'))

    http = HttpMockSequence([
      ({'status': '200'}, """{ "access_token":"SlAV32hkKG",
       "refresh_token":"8xLOxBtZp8",
       "id_token": "%s"}""" % jwt),
      ])

    credentials = self.flow.step2_exchange('some random code', http)
    self.assertEqual(credentials.id_token, body)

class CredentialsFromCodeTests(unittest.TestCase):
  def setUp(self):
    self.client_id = 'client_id_abc'
    self.client_secret = 'secret_use_code'
    self.scope = 'foo'
    self.code = '12345abcde'
    self.redirect_uri = 'postmessage'

  def test_exchange_code_for_token(self):
    http = HttpMockSequence([
      ({'status': '200'},
      """{ "access_token":"asdfghjkl",
       "expires_in":3600 }"""),
    ])
    credentials = credentials_from_code(self.client_id, self.client_secret,
                                    self.scope, self.code, self.redirect_uri,
                                    http)
    self.assertEquals(credentials.access_token, 'asdfghjkl')
    self.assertNotEqual(None, credentials.token_expiry)

  def test_exchange_code_for_token_fail(self):
    http = HttpMockSequence([
      ({'status': '400'}, '{"error":"invalid_request"}'),
      ])

    try:
      credentials = credentials_from_code(self.client_id, self.client_secret,
                                      self.scope, self.code, self.redirect_uri,
                                      http)
      self.fail("should raise exception if exchange doesn't get 200")
    except FlowExchangeError:
      pass


  def test_exchange_code_and_file_for_token(self):
    http = HttpMockSequence([
      ({'status': '200'},
      """{ "access_token":"asdfghjkl",
       "expires_in":3600 }"""),
    ])
    credentials = credentials_from_clientsecrets_and_code(
                            datafile('client_secrets.json'), self.scope,
                            self.code, http=http)
    self.assertEquals(credentials.access_token, 'asdfghjkl')
    self.assertNotEqual(None, credentials.token_expiry)

  def test_exchange_code_and_file_for_token_fail(self):
    http = HttpMockSequence([
      ({'status': '400'}, '{"error":"invalid_request"}'),
      ])

    try:
      credentials = credentials_from_clientsecrets_and_code(
                            datafile('client_secrets.json'), self.scope,
                            self.code, http=http)
      self.fail("should raise exception if exchange doesn't get 200")
    except FlowExchangeError:
      pass



class MemoryCacheTests(unittest.TestCase):

  def test_get_set_delete(self):
    m = MemoryCache()
    self.assertEqual(None, m.get('foo'))
    self.assertEqual(None, m.delete('foo'))
    m.set('foo', 'bar')
    self.assertEqual('bar', m.get('foo'))
    m.delete('foo')
    self.assertEqual(None, m.get('foo'))


if __name__ == '__main__':
  unittest.main()
