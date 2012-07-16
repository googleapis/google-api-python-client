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

"""Unit tests for oauth2client.clientsecrets."""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'


import os
import unittest
import StringIO

import httplib2

from oauth2client import clientsecrets


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
VALID_FILE = os.path.join(DATA_DIR, 'client_secrets.json')
INVALID_FILE = os.path.join(DATA_DIR, 'unfilled_client_secrets.json')
NONEXISTENT_FILE = os.path.join(__file__, '..', 'afilethatisntthere.json')

class OAuth2CredentialsTests(unittest.TestCase):

  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_validate_error(self):
    ERRORS = [
      ('{}', 'Invalid'),
      ('{"foo": {}}', 'Unknown'),
      ('{"web": {}}', 'Missing'),
      ('{"web": {"client_id": "dkkd"}}', 'Missing'),
      ("""{
         "web": {
           "client_id": "[[CLIENT ID REQUIRED]]",
           "client_secret": "[[CLIENT SECRET REQUIRED]]",
           "redirect_uris": ["http://localhost:8080/oauth2callback"],
           "auth_uri": "",
           "token_uri": ""
         }
       }
       """, 'Property'),
      ]
    for src, match in ERRORS:
      # Test load(s)
      try:
        clientsecrets.loads(src)
        self.fail(src + ' should not be a valid client_secrets file.')
      except clientsecrets.InvalidClientSecretsError, e:
        self.assertTrue(str(e).startswith(match))

      # Test loads(fp)
      try:
        fp = StringIO.StringIO(src)
        clientsecrets.load(fp)
        self.fail(src + ' should not be a valid client_secrets file.')
      except clientsecrets.InvalidClientSecretsError, e:
        self.assertTrue(str(e).startswith(match))

  def test_load_by_filename(self):
    try:
      clientsecrets._loadfile(NONEXISTENT_FILE)
      self.fail('should fail to load a missing client_secrets file.')
    except clientsecrets.InvalidClientSecretsError, e:
      self.assertTrue(str(e).startswith('File'))


class CachedClientsecretsTests(unittest.TestCase):

  class CacheMock(object):
    def __init__(self):
      self.cache = {}
      self.last_get_ns = None
      self.last_set_ns = None

    def get(self, key, namespace=''):
      # ignoring namespace for easier testing
      self.last_get_ns = namespace
      return self.cache.get(key, None)

    def set(self, key, value, namespace=''):
      # ignoring namespace for easier testing
      self.last_set_ns = namespace
      self.cache[key] = value

  def setUp(self):
    self.cache_mock = self.CacheMock()

  def test_cache_miss(self):
    client_type, client_info = clientsecrets.loadfile(
      VALID_FILE, cache=self.cache_mock)
    self.assertEquals('web', client_type)
    self.assertEquals('foo_client_secret', client_info['client_secret'])

    cached = self.cache_mock.cache[VALID_FILE]
    self.assertEquals({client_type: client_info}, cached)

    # make sure we're using non-empty namespace
    ns = self.cache_mock.last_set_ns
    self.assertTrue(bool(ns))
    # make sure they're equal
    self.assertEquals(ns, self.cache_mock.last_get_ns)

  def test_cache_hit(self):
    self.cache_mock.cache[NONEXISTENT_FILE] = { 'web': 'secret info' }

    client_type, client_info = clientsecrets.loadfile(
      NONEXISTENT_FILE, cache=self.cache_mock)
    self.assertEquals('web', client_type)
    self.assertEquals('secret info', client_info)
    # make sure we didn't do any set() RPCs
    self.assertEqual(None, self.cache_mock.last_set_ns)

  def test_validation(self):
    try:
      clientsecrets.loadfile(INVALID_FILE, cache=self.cache_mock)
      self.fail('Expected InvalidClientSecretsError to be raised '
                'while loading %s' % INVALID_FILE)
    except clientsecrets.InvalidClientSecretsError:
      pass

  def test_without_cache(self):
    # this also ensures loadfile() is backward compatible
    client_type, client_info = clientsecrets.loadfile(VALID_FILE)
    self.assertEquals('web', client_type)
    self.assertEquals('foo_client_secret', client_info['client_secret'])


if __name__ == '__main__':
  unittest.main()
