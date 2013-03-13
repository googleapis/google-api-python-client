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
import os
import sys
import tempfile
import time
import unittest
import urlparse

try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

from apiclient.http import HttpMockSequence
from oauth2client import crypt
from oauth2client.anyjson import simplejson
from oauth2client.client import Credentials
from oauth2client.client import SignedJwtAssertionCredentials
from oauth2client.client import VerifyJwtTokenError
from oauth2client.client import verify_id_token
from oauth2client.client import HAS_OPENSSL
from oauth2client.client import HAS_CRYPTO
from oauth2client.file import Storage


def datafile(filename):
  f = open(os.path.join(os.path.dirname(__file__), 'data', filename), 'r')
  data = f.read()
  f.close()
  return data


class CryptTests(unittest.TestCase):
  def setUp(self):
    self.format = 'p12'
    self.signer = crypt.OpenSSLSigner
    self.verifier = crypt.OpenSSLVerifier

  def test_sign_and_verify(self):
    private_key = datafile('privatekey.%s' % self.format)
    public_key = datafile('publickey.pem')

    signer = self.signer.from_string(private_key)
    signature = signer.sign('foo')

    verifier = self.verifier.from_string(public_key, True)

    self.assertTrue(verifier.verify('foo', signature))

    self.assertFalse(verifier.verify('bar', signature))
    self.assertFalse(verifier.verify('foo', 'bad signagure'))

  def _check_jwt_failure(self, jwt, expected_error):
      try:
          public_key = datafile('publickey.pem')
          certs = {'foo': public_key}
          audience = 'https://www.googleapis.com/auth/id?client_id=' + \
              'external_public_key@testing.gserviceaccount.com'
          contents = crypt.verify_signed_jwt_with_certs(jwt, certs, audience)
          self.fail('Should have thrown for %s' % jwt)
      except:
          e = sys.exc_info()[1]
          msg = e.args[0]
          self.assertTrue(expected_error in msg)

  def _create_signed_jwt(self):
    private_key = datafile('privatekey.%s' % self.format)
    signer = self.signer.from_string(private_key)
    audience = 'some_audience_address@testing.gserviceaccount.com'
    now = long(time.time())

    return crypt.make_signed_jwt(
        signer,
        {
        'aud': audience,
        'iat': now,
        'exp': now + 300,
        'user': 'billy bob',
        'metadata': {'meta': 'data'},
        })

  def test_verify_id_token(self):
    jwt = self._create_signed_jwt()
    public_key = datafile('publickey.pem')
    certs = {'foo': public_key }
    audience = 'some_audience_address@testing.gserviceaccount.com'
    contents = crypt.verify_signed_jwt_with_certs(jwt, certs, audience)
    self.assertEqual('billy bob', contents['user'])
    self.assertEqual('data', contents['metadata']['meta'])

  def test_verify_id_token_with_certs_uri(self):
    jwt = self._create_signed_jwt()

    http = HttpMockSequence([
      ({'status': '200'}, datafile('certs.json')),
      ])

    contents = verify_id_token(jwt,
        'some_audience_address@testing.gserviceaccount.com', http=http)
    self.assertEqual('billy bob', contents['user'])
    self.assertEqual('data', contents['metadata']['meta'])

  def test_verify_id_token_with_certs_uri_fails(self):
    jwt = self._create_signed_jwt()

    http = HttpMockSequence([
      ({'status': '404'}, datafile('certs.json')),
      ])

    self.assertRaises(VerifyJwtTokenError, verify_id_token, jwt,
        'some_audience_address@testing.gserviceaccount.com', http=http)

  def test_verify_id_token_bad_tokens(self):
    private_key = datafile('privatekey.%s' % self.format)

    # Wrong number of segments
    self._check_jwt_failure('foo', 'Wrong number of segments')

    # Not json
    self._check_jwt_failure('foo.bar.baz',
        'Can\'t parse token')

    # Bad signature
    jwt = 'foo.%s.baz' % crypt._urlsafe_b64encode('{"a":"b"}')
    self._check_jwt_failure(jwt, 'Invalid token signature')

    # No expiration
    signer = self.signer.from_string(private_key)
    audience = 'https:#www.googleapis.com/auth/id?client_id=' + \
        'external_public_key@testing.gserviceaccount.com'
    jwt = crypt.make_signed_jwt(signer, {
          'aud': 'audience',
          'iat': time.time(),
          }
        )
    self._check_jwt_failure(jwt, 'No exp field in token')

    # No issued at
    jwt = crypt.make_signed_jwt(signer, {
          'aud': 'audience',
          'exp': time.time() + 400,
        }
      )
    self._check_jwt_failure(jwt, 'No iat field in token')

    # Too early
    jwt = crypt.make_signed_jwt(signer, {
        'aud': 'audience',
        'iat': time.time() + 301,
        'exp': time.time() + 400,
    })
    self._check_jwt_failure(jwt, 'Token used too early')

    # Too late
    jwt = crypt.make_signed_jwt(signer, {
        'aud': 'audience',
        'iat': time.time() - 500,
        'exp': time.time() - 301,
    })
    self._check_jwt_failure(jwt, 'Token used too late')

    # Wrong target
    jwt = crypt.make_signed_jwt(signer, {
        'aud': 'somebody else',
        'iat': time.time(),
        'exp': time.time() + 300,
    })
    self._check_jwt_failure(jwt, 'Wrong recipient')


class PEMCryptTestsPyCrypto(CryptTests):
  def setUp(self):
    self.format = 'pem'
    self.signer = crypt.PyCryptoSigner
    self.verifier = crypt.OpenSSLVerifier


class PEMCryptTestsOpenSSL(CryptTests):
  def setUp(self):
    self.format = 'pem'
    self.signer = crypt.OpenSSLSigner
    self.verifier = crypt.OpenSSLVerifier


class SignedJwtAssertionCredentialsTests(unittest.TestCase):
  def setUp(self):
    self.format = 'p12'
    crypt.Signer = crypt.OpenSSLSigner

  def test_credentials_good(self):
    private_key = datafile('privatekey.%s' % self.format)
    credentials = SignedJwtAssertionCredentials(
        'some_account@example.com',
        private_key,
        scope='read+write',
        sub='joe@example.org')
    http = HttpMockSequence([
      ({'status': '200'}, '{"access_token":"1/3w","expires_in":3600}'),
      ({'status': '200'}, 'echo_request_headers'),
      ])
    http = credentials.authorize(http)
    resp, content = http.request('http://example.org')
    self.assertEqual('Bearer 1/3w', content['Authorization'])

  def test_credentials_to_from_json(self):
    private_key = datafile('privatekey.%s' % self.format)
    credentials = SignedJwtAssertionCredentials(
        'some_account@example.com',
        private_key,
        scope='read+write',
        sub='joe@example.org')
    json = credentials.to_json()
    restored = Credentials.new_from_json(json)
    self.assertEqual(credentials.private_key, restored.private_key)
    self.assertEqual(credentials.private_key_password,
                     restored.private_key_password)
    self.assertEqual(credentials.kwargs, restored.kwargs)

  def _credentials_refresh(self, credentials):
    http = HttpMockSequence([
      ({'status': '200'}, '{"access_token":"1/3w","expires_in":3600}'),
      ({'status': '401'}, ''),
      ({'status': '200'}, '{"access_token":"3/3w","expires_in":3600}'),
      ({'status': '200'}, 'echo_request_headers'),
      ])
    http = credentials.authorize(http)
    resp, content = http.request('http://example.org')
    return content

  def test_credentials_refresh_without_storage(self):
    private_key = datafile('privatekey.%s' % self.format)
    credentials = SignedJwtAssertionCredentials(
        'some_account@example.com',
        private_key,
        scope='read+write',
        sub='joe@example.org')

    content = self._credentials_refresh(credentials)

    self.assertEqual('Bearer 3/3w', content['Authorization'])

  def test_credentials_refresh_with_storage(self):
    private_key = datafile('privatekey.%s' % self.format)
    credentials = SignedJwtAssertionCredentials(
        'some_account@example.com',
        private_key,
        scope='read+write',
        sub='joe@example.org')

    (filehandle, filename) = tempfile.mkstemp()
    os.close(filehandle)
    store = Storage(filename)
    store.put(credentials)
    credentials.set_store(store)

    content = self._credentials_refresh(credentials)

    self.assertEqual('Bearer 3/3w', content['Authorization'])
    os.unlink(filename)


class PEMSignedJwtAssertionCredentialsOpenSSLTests(
    SignedJwtAssertionCredentialsTests):
  def setUp(self):
    self.format = 'pem'
    crypt.Signer = crypt.OpenSSLSigner


class PEMSignedJwtAssertionCredentialsPyCryptoTests(
    SignedJwtAssertionCredentialsTests):
  def setUp(self):
    self.format = 'pem'
    crypt.Signer = crypt.PyCryptoSigner


class PKCSSignedJwtAssertionCredentialsPyCryptoTests(unittest.TestCase):
  def test_for_failure(self):
    crypt.Signer = crypt.PyCryptoSigner
    private_key = datafile('privatekey.p12')
    credentials = SignedJwtAssertionCredentials(
        'some_account@example.com',
        private_key,
        scope='read+write',
        sub='joe@example.org')
    try:
      credentials._generate_assertion()
      self.fail()
    except NotImplementedError:
      pass

class TestHasOpenSSLFlag(unittest.TestCase):
  def test_true(self):
    self.assertEqual(True, HAS_OPENSSL)
    self.assertEqual(True, HAS_CRYPTO)

if __name__ == '__main__':
  unittest.main()
