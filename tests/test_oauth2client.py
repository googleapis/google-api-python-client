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

from apiclient.http import HttpMock
from apiclient.http import HttpMockSequence
from oauth2client import GOOGLE_REVOKE_URI
from oauth2client import GOOGLE_TOKEN_URI
from oauth2client.anyjson import simplejson
from oauth2client.client import AccessTokenCredentials
from oauth2client.client import AccessTokenCredentialsError
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import AssertionCredentials
from oauth2client.client import Credentials
from oauth2client.client import FlowExchangeError
from oauth2client.client import MemoryCache
from oauth2client.client import NonAsciiHeaderError
from oauth2client.client import OAuth2Credentials
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import OOB_CALLBACK_URN
from oauth2client.client import REFRESH_STATUS_CODES
from oauth2client.client import Storage
from oauth2client.client import TokenRevokeError
from oauth2client.client import VerifyJwtTokenError
from oauth2client.client import _extract_id_token
from oauth2client.client import _update_query_params
from oauth2client.client import credentials_from_clientsecrets_and_code
from oauth2client.client import credentials_from_code
from oauth2client.client import flow_from_clientsecrets
from oauth2client.clientsecrets import _loadfile
from test_discovery import assertUrisEqual


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


def datafile(filename):
  return os.path.join(DATA_DIR, filename)


def load_and_cache(existing_file, fakename, cache_mock):
  client_type, client_info = _loadfile(datafile(existing_file))
  cache_mock.cache[fakename] = {client_type: client_info}


class CacheMock(object):
    def __init__(self):
      self.cache = {}

    def get(self, key, namespace=''):
      # ignoring namespace for easier testing
      return self.cache.get(key, None)

    def set(self, key, value, namespace=''):
      # ignoring namespace for easier testing
      self.cache[key] = value


class CredentialsTests(unittest.TestCase):

  def test_to_from_json(self):
    credentials = Credentials()
    json = credentials.to_json()
    restored = Credentials.new_from_json(json)


class DummyDeleteStorage(Storage):
  delete_called = False

  def locked_delete(self):
    self.delete_called = True


def _token_revoke_test_helper(testcase, status, revoke_raise,
                              valid_bool_value, token_attr):
  current_store = getattr(testcase.credentials, 'store', None)

  dummy_store = DummyDeleteStorage()
  testcase.credentials.set_store(dummy_store)

  actual_do_revoke = testcase.credentials._do_revoke
  testcase.token_from_revoke = None
  def do_revoke_stub(http_request, token):
    testcase.token_from_revoke = token
    return actual_do_revoke(http_request, token)
  testcase.credentials._do_revoke = do_revoke_stub

  http = HttpMock(headers={'status': status})
  if revoke_raise:
    testcase.assertRaises(TokenRevokeError, testcase.credentials.revoke, http)
  else:
    testcase.credentials.revoke(http)

  testcase.assertEqual(getattr(testcase.credentials, token_attr),
                       testcase.token_from_revoke)
  testcase.assertEqual(valid_bool_value, testcase.credentials.invalid)
  testcase.assertEqual(valid_bool_value, dummy_store.delete_called)

  testcase.credentials.set_store(current_store)


class BasicCredentialsTests(unittest.TestCase):

  def setUp(self):
    access_token = 'foo'
    client_id = 'some_client_id'
    client_secret = 'cOuDdkfjxxnv+'
    refresh_token = '1/0/a.df219fjls0'
    token_expiry = datetime.datetime.utcnow()
    user_agent = 'refresh_checker/1.0'
    self.credentials = OAuth2Credentials(
        access_token, client_id, client_secret,
        refresh_token, token_expiry, GOOGLE_TOKEN_URI,
        user_agent, revoke_uri=GOOGLE_REVOKE_URI)

  def test_token_refresh_success(self):
    for status_code in REFRESH_STATUS_CODES:
      token_response = {'access_token': '1/3w', 'expires_in': 3600}
      http = HttpMockSequence([
          ({'status': status_code}, ''),
          ({'status': '200'}, simplejson.dumps(token_response)),
          ({'status': '200'}, 'echo_request_headers'),
      ])
      http = self.credentials.authorize(http)
      resp, content = http.request('http://example.com')
      self.assertEqual('Bearer 1/3w', content['Authorization'])
      self.assertFalse(self.credentials.access_token_expired)
      self.assertEqual(token_response, self.credentials.token_response)

  def test_token_refresh_failure(self):
    for status_code in REFRESH_STATUS_CODES:
      http = HttpMockSequence([
        ({'status': status_code}, ''),
        ({'status': '400'}, '{"error":"access_denied"}'),
        ])
      http = self.credentials.authorize(http)
      try:
        http.request('http://example.com')
        self.fail('should raise AccessTokenRefreshError exception')
      except AccessTokenRefreshError:
        pass
      self.assertTrue(self.credentials.access_token_expired)
      self.assertEqual(None, self.credentials.token_response)

  def test_token_revoke_success(self):
    _token_revoke_test_helper(
        self, '200', revoke_raise=False,
        valid_bool_value=True, token_attr='refresh_token')

  def test_token_revoke_failure(self):
    _token_revoke_test_helper(
        self, '400', revoke_raise=True,
        valid_bool_value=False, token_attr='refresh_token')

  def test_non_401_error_response(self):
    http = HttpMockSequence([
      ({'status': '400'}, ''),
      ])
    http = self.credentials.authorize(http)
    resp, content = http.request('http://example.com')
    self.assertEqual(400, resp.status)
    self.assertEqual(None, self.credentials.token_response)

  def test_to_from_json(self):
    json = self.credentials.to_json()
    instance = OAuth2Credentials.from_json(json)
    self.assertEqual(OAuth2Credentials, type(instance))
    instance.token_expiry = None
    self.credentials.token_expiry = None

    self.assertEqual(instance.__dict__, self.credentials.__dict__)

  def test_no_unicode_in_request_params(self):
    access_token = u'foo'
    client_id = u'some_client_id'
    client_secret = u'cOuDdkfjxxnv+'
    refresh_token = u'1/0/a.df219fjls0'
    token_expiry = unicode(datetime.datetime.utcnow())
    token_uri = unicode(GOOGLE_TOKEN_URI)
    revoke_uri = unicode(GOOGLE_REVOKE_URI)
    user_agent = u'refresh_checker/1.0'
    credentials = OAuth2Credentials(access_token, client_id, client_secret,
                                    refresh_token, token_expiry, token_uri,
                                    user_agent, revoke_uri=revoke_uri)

    http = HttpMock(headers={'status': '200'})
    http = credentials.authorize(http)
    http.request(u'http://example.com', method=u'GET', headers={u'foo': u'bar'})
    for k, v in http.headers.iteritems():
      self.assertEqual(str, type(k))
      self.assertEqual(str, type(v))

    # Test again with unicode strings that can't simple be converted to ASCII.
    try:
      http.request(
          u'http://example.com', method=u'GET', headers={u'foo': u'\N{COMET}'})
      self.fail('Expected exception to be raised.')
    except NonAsciiHeaderError:
      pass

    self.credentials.token_response = 'foobar'
    instance = OAuth2Credentials.from_json(self.credentials.to_json())
    self.assertEqual('foobar', instance.token_response)


class AccessTokenCredentialsTests(unittest.TestCase):

  def setUp(self):
    access_token = 'foo'
    user_agent = 'refresh_checker/1.0'
    self.credentials = AccessTokenCredentials(access_token, user_agent,
                                              revoke_uri=GOOGLE_REVOKE_URI)

  def test_token_refresh_success(self):
    for status_code in REFRESH_STATUS_CODES:
      http = HttpMockSequence([
        ({'status': status_code}, ''),
        ])
      http = self.credentials.authorize(http)
      try:
        resp, content = http.request('http://example.com')
        self.fail('should throw exception if token expires')
      except AccessTokenCredentialsError:
        pass
      except Exception:
        self.fail('should only throw AccessTokenCredentialsError')

  def test_token_revoke_success(self):
    _token_revoke_test_helper(
        self, '200', revoke_raise=False,
        valid_bool_value=True, token_attr='access_token')

  def test_token_revoke_failure(self):
    _token_revoke_test_helper(
        self, '400', revoke_raise=True,
        valid_bool_value=False, token_attr='access_token')

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
  assertion_text = 'This is the assertion'
  assertion_type = 'http://www.google.com/assertionType'

  class AssertionCredentialsTestImpl(AssertionCredentials):

    def _generate_assertion(self):
      return TestAssertionCredentials.assertion_text

  def setUp(self):
    user_agent = 'fun/2.0'
    self.credentials = self.AssertionCredentialsTestImpl(self.assertion_type,
        user_agent=user_agent)

  def test_assertion_body(self):
    body = urlparse.parse_qs(self.credentials._generate_refresh_request_body())
    self.assertEqual(self.assertion_text, body['assertion'][0])
    self.assertEqual('urn:ietf:params:oauth:grant-type:jwt-bearer',
                     body['grant_type'][0])

  def test_assertion_refresh(self):
    http = HttpMockSequence([
      ({'status': '200'}, '{"access_token":"1/3w"}'),
      ({'status': '200'}, 'echo_request_headers'),
      ])
    http = self.credentials.authorize(http)
    resp, content = http.request('http://example.com')
    self.assertEqual('Bearer 1/3w', content['Authorization'])

  def test_token_revoke_success(self):
    _token_revoke_test_helper(
        self, '200', revoke_raise=False,
        valid_bool_value=True, token_attr='access_token')

  def test_token_revoke_failure(self):
    _token_revoke_test_helper(
        self, '400', revoke_raise=True,
        valid_bool_value=False, token_attr='access_token')


class UpdateQueryParamsTest(unittest.TestCase):
  def test_update_query_params_no_params(self):
    uri = 'http://www.google.com'
    updated = _update_query_params(uri, {'a': 'b'})
    self.assertEqual(updated, uri + '?a=b')

  def test_update_query_params_existing_params(self):
    uri = 'http://www.google.com?x=y'
    updated = _update_query_params(uri, {'a': 'b', 'c': 'd&'})
    hardcoded_update = uri + '&a=b&c=d%26'
    assertUrisEqual(self, updated, hardcoded_update)


class ExtractIdTokenTest(unittest.TestCase):
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
        redirect_uri=OOB_CALLBACK_URN,
        user_agent='unittest-sample/1.0',
        revoke_uri='dummy_revoke_uri',
        )

  def test_construct_authorize_url(self):
    authorize_url = self.flow.step1_get_authorize_url()

    parsed = urlparse.urlparse(authorize_url)
    q = urlparse.parse_qs(parsed[4])
    self.assertEqual('client_id+1', q['client_id'][0])
    self.assertEqual('code', q['response_type'][0])
    self.assertEqual('foo', q['scope'][0])
    self.assertEqual(OOB_CALLBACK_URN, q['redirect_uri'][0])
    self.assertEqual('offline', q['access_type'][0])

  def test_override_flow_via_kwargs(self):
    """Passing kwargs to override defaults."""
    flow = OAuth2WebServerFlow(
        client_id='client_id+1',
        client_secret='secret+1',
        scope='foo',
        redirect_uri=OOB_CALLBACK_URN,
        user_agent='unittest-sample/1.0',
        access_type='online',
        response_type='token'
        )
    authorize_url = flow.step1_get_authorize_url()

    parsed = urlparse.urlparse(authorize_url)
    q = urlparse.parse_qs(parsed[4])
    self.assertEqual('client_id+1', q['client_id'][0])
    self.assertEqual('token', q['response_type'][0])
    self.assertEqual('foo', q['scope'][0])
    self.assertEqual(OOB_CALLBACK_URN, q['redirect_uri'][0])
    self.assertEqual('online', q['access_type'][0])

  def test_exchange_failure(self):
    http = HttpMockSequence([
      ({'status': '400'}, '{"error":"invalid_request"}'),
      ])

    try:
      credentials = self.flow.step2_exchange('some random code', http=http)
      self.fail('should raise exception if exchange doesn\'t get 200')
    except FlowExchangeError:
      pass

  def test_urlencoded_exchange_failure(self):
    http = HttpMockSequence([
      ({'status': '400'}, 'error=invalid_request'),
    ])

    try:
      credentials = self.flow.step2_exchange('some random code', http=http)
      self.fail('should raise exception if exchange doesn\'t get 200')
    except FlowExchangeError, e:
      self.assertEquals('invalid_request', str(e))

  def test_exchange_failure_with_json_error(self):
    # Some providers have 'error' attribute as a JSON object
    # in place of regular string.
    # This test makes sure no strange object-to-string coversion
    # exceptions are being raised instead of FlowExchangeError.
    http = HttpMockSequence([
      ({'status': '400'},
      """ {"error": {
              "type": "OAuthException",
              "message": "Error validating verification code."} }"""),
      ])

    try:
      credentials = self.flow.step2_exchange('some random code', http=http)
      self.fail('should raise exception if exchange doesn\'t get 200')
    except FlowExchangeError, e:
      pass

  def test_exchange_success(self):
    http = HttpMockSequence([
      ({'status': '200'},
      """{ "access_token":"SlAV32hkKG",
       "expires_in":3600,
       "refresh_token":"8xLOxBtZp8" }"""),
      ])

    credentials = self.flow.step2_exchange('some random code', http=http)
    self.assertEqual('SlAV32hkKG', credentials.access_token)
    self.assertNotEqual(None, credentials.token_expiry)
    self.assertEqual('8xLOxBtZp8', credentials.refresh_token)
    self.assertEqual('dummy_revoke_uri', credentials.revoke_uri)

  def test_urlencoded_exchange_success(self):
    http = HttpMockSequence([
      ({'status': '200'}, 'access_token=SlAV32hkKG&expires_in=3600'),
    ])

    credentials = self.flow.step2_exchange('some random code', http=http)
    self.assertEqual('SlAV32hkKG', credentials.access_token)
    self.assertNotEqual(None, credentials.token_expiry)

  def test_urlencoded_expires_param(self):
    http = HttpMockSequence([
      # Note the 'expires=3600' where you'd normally
      # have if named 'expires_in'
      ({'status': '200'}, 'access_token=SlAV32hkKG&expires=3600'),
    ])

    credentials = self.flow.step2_exchange('some random code', http=http)
    self.assertNotEqual(None, credentials.token_expiry)

  def test_exchange_no_expires_in(self):
    http = HttpMockSequence([
      ({'status': '200'}, """{ "access_token":"SlAV32hkKG",
       "refresh_token":"8xLOxBtZp8" }"""),
      ])

    credentials = self.flow.step2_exchange('some random code', http=http)
    self.assertEqual(None, credentials.token_expiry)

  def test_urlencoded_exchange_no_expires_in(self):
    http = HttpMockSequence([
      # This might be redundant but just to make sure
      # urlencoded access_token gets parsed correctly
      ({'status': '200'}, 'access_token=SlAV32hkKG'),
    ])

    credentials = self.flow.step2_exchange('some random code', http=http)
    self.assertEqual(None, credentials.token_expiry)

  def test_exchange_fails_if_no_code(self):
    http = HttpMockSequence([
      ({'status': '200'}, """{ "access_token":"SlAV32hkKG",
       "refresh_token":"8xLOxBtZp8" }"""),
      ])

    code = {'error': 'thou shall not pass'}
    try:
      credentials = self.flow.step2_exchange(code, http=http)
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
      'some random code', http=http)

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

    credentials = self.flow.step2_exchange('some random code', http=http)
    self.assertEqual(credentials.id_token, body)


class FlowFromCachedClientsecrets(unittest.TestCase):

  def test_flow_from_clientsecrets_cached(self):
    cache_mock = CacheMock()
    load_and_cache('client_secrets.json', 'some_secrets', cache_mock)

    flow = flow_from_clientsecrets(
        'some_secrets', '', redirect_uri='oob', cache=cache_mock)
    self.assertEquals('foo_client_secret', flow.client_secret)


class CredentialsFromCodeTests(unittest.TestCase):
  def setUp(self):
    self.client_id = 'client_id_abc'
    self.client_secret = 'secret_use_code'
    self.scope = 'foo'
    self.code = '12345abcde'
    self.redirect_uri = 'postmessage'

  def test_exchange_code_for_token(self):
    token = 'asdfghjkl'
    payload =simplejson.dumps({'access_token': token, 'expires_in': 3600})
    http = HttpMockSequence([
      ({'status': '200'}, payload),
    ])
    credentials = credentials_from_code(self.client_id, self.client_secret,
        self.scope, self.code, redirect_uri=self.redirect_uri,
        http=http)
    self.assertEquals(credentials.access_token, token)
    self.assertNotEqual(None, credentials.token_expiry)

  def test_exchange_code_for_token_fail(self):
    http = HttpMockSequence([
      ({'status': '400'}, '{"error":"invalid_request"}'),
      ])

    try:
      credentials = credentials_from_code(self.client_id, self.client_secret,
          self.scope, self.code, redirect_uri=self.redirect_uri,
          http=http)
      self.fail('should raise exception if exchange doesn\'t get 200')
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

  def test_exchange_code_and_cached_file_for_token(self):
    http = HttpMockSequence([
      ({'status': '200'}, '{ "access_token":"asdfghjkl"}'),
      ])
    cache_mock = CacheMock()
    load_and_cache('client_secrets.json', 'some_secrets', cache_mock)

    credentials = credentials_from_clientsecrets_and_code(
        'some_secrets', self.scope,
        self.code, http=http, cache=cache_mock)
    self.assertEquals(credentials.access_token, 'asdfghjkl')

  def test_exchange_code_and_file_for_token_fail(self):
    http = HttpMockSequence([
      ({'status': '400'}, '{"error":"invalid_request"}'),
      ])

    try:
      credentials = credentials_from_clientsecrets_and_code(
                            datafile('client_secrets.json'), self.scope,
                            self.code, http=http)
      self.fail('should raise exception if exchange doesn\'t get 200')
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
