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


"""Oauth2client.file tests

Unit tests for oauth2client.file
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import copy
import datetime
import httplib2
import os
import pickle
import stat
import tempfile
import unittest

from apiclient.http import HttpMockSequence
from oauth2client import multistore_file
from oauth2client.anyjson import simplejson
from oauth2client.client import AccessTokenCredentials
from oauth2client.client import AssertionCredentials
from oauth2client.client import OAuth2Credentials
from oauth2client.file import Storage


FILENAME = tempfile.mktemp('oauth2client_test.data')


class OAuth2ClientFileTests(unittest.TestCase):

  def tearDown(self):
    try:
      os.unlink(FILENAME)
    except OSError:
      pass

  def setUp(self):
    try:
      os.unlink(FILENAME)
    except OSError:
      pass

  def test_non_existent_file_storage(self):
    s = Storage(FILENAME)
    credentials = s.get()
    self.assertEquals(None, credentials)

  def test_pickle_and_json_interop(self):
    # Write a file with a pickled OAuth2Credentials.
    access_token = 'foo'
    client_id = 'some_client_id'
    client_secret = 'cOuDdkfjxxnv+'
    refresh_token = '1/0/a.df219fjls0'
    token_expiry = datetime.datetime.utcnow()
    token_uri = 'https://www.google.com/accounts/o8/oauth2/token'
    user_agent = 'refresh_checker/1.0'

    credentials = OAuth2Credentials(
        access_token, client_id, client_secret,
        refresh_token, token_expiry, token_uri,
        user_agent)

    f = open(FILENAME, 'w')
    pickle.dump(credentials, f)
    f.close()

    # Storage should be not be able to read that object, as the capability to
    # read and write credentials as pickled objects has been removed.
    s = Storage(FILENAME)
    read_credentials = s.get()
    self.assertEquals(None, read_credentials)

    # Now write it back out and confirm it has been rewritten as JSON
    s.put(credentials)
    f = file(FILENAME)
    data = simplejson.load(f)
    f.close()

    self.assertEquals(data['access_token'], 'foo')
    self.assertEquals(data['_class'], 'OAuth2Credentials')
    self.assertEquals(data['_module'], OAuth2Credentials.__module__)

  def test_token_refresh(self):
    access_token = 'foo'
    client_id = 'some_client_id'
    client_secret = 'cOuDdkfjxxnv+'
    refresh_token = '1/0/a.df219fjls0'
    token_expiry = datetime.datetime.utcnow()
    token_uri = 'https://www.google.com/accounts/o8/oauth2/token'
    user_agent = 'refresh_checker/1.0'

    credentials = OAuth2Credentials(
        access_token, client_id, client_secret,
        refresh_token, token_expiry, token_uri,
        user_agent)

    s = Storage(FILENAME)
    s.put(credentials)
    credentials = s.get()
    new_cred = copy.copy(credentials)
    new_cred.access_token = 'bar'
    s.put(new_cred)

    credentials._refresh(lambda x: x)
    self.assertEquals(credentials.access_token, 'bar')

  def test_credentials_delete(self):
    access_token = 'foo'
    client_id = 'some_client_id'
    client_secret = 'cOuDdkfjxxnv+'
    refresh_token = '1/0/a.df219fjls0'
    token_expiry = datetime.datetime.utcnow()
    token_uri = 'https://www.google.com/accounts/o8/oauth2/token'
    user_agent = 'refresh_checker/1.0'

    credentials = OAuth2Credentials(
        access_token, client_id, client_secret,
        refresh_token, token_expiry, token_uri,
        user_agent)

    s = Storage(FILENAME)
    s.put(credentials)
    credentials = s.get()
    self.assertNotEquals(None, credentials)
    s.delete()
    credentials = s.get()
    self.assertEquals(None, credentials)

  def test_access_token_credentials(self):
    access_token = 'foo'
    user_agent = 'refresh_checker/1.0'

    credentials = AccessTokenCredentials(access_token, user_agent)

    s = Storage(FILENAME)
    credentials = s.put(credentials)
    credentials = s.get()

    self.assertNotEquals(None, credentials)
    self.assertEquals('foo', credentials.access_token)
    mode = os.stat(FILENAME).st_mode

    if os.name == 'posix':
      self.assertEquals('0600', oct(stat.S_IMODE(os.stat(FILENAME).st_mode)))

  def test_read_only_file_fail_lock(self):
    access_token = 'foo'
    client_secret = 'cOuDdkfjxxnv+'
    refresh_token = '1/0/a.df219fjls0'
    token_expiry = datetime.datetime.utcnow()
    token_uri = 'https://www.google.com/accounts/o8/oauth2/token'
    user_agent = 'refresh_checker/1.0'
    client_id = 'some_client_id'

    credentials = OAuth2Credentials(
        access_token, client_id, client_secret,
        refresh_token, token_expiry, token_uri,
        user_agent)

    open(FILENAME, 'a+b').close()
    os.chmod(FILENAME, 0400)

    store = multistore_file.get_credential_storage(
        FILENAME,
        credentials.client_id,
        credentials.user_agent,
        ['some-scope', 'some-other-scope'])

    store.put(credentials)
    if os.name == 'posix':
      self.assertTrue(store._multistore._read_only)
    os.chmod(FILENAME, 0600)


  def test_multistore_non_existent_file(self):
    store = multistore_file.get_credential_storage(
        FILENAME,
        'some_client_id',
        'user-agent/1.0',
        ['some-scope', 'some-other-scope'])

    credentials = store.get()
    self.assertEquals(None, credentials)

  def test_multistore_file(self):
    access_token = 'foo'
    client_secret = 'cOuDdkfjxxnv+'
    refresh_token = '1/0/a.df219fjls0'
    token_expiry = datetime.datetime.utcnow()
    token_uri = 'https://www.google.com/accounts/o8/oauth2/token'
    user_agent = 'refresh_checker/1.0'
    client_id = 'some_client_id'

    credentials = OAuth2Credentials(
        access_token, client_id, client_secret,
        refresh_token, token_expiry, token_uri,
        user_agent)

    store = multistore_file.get_credential_storage(
        FILENAME,
        credentials.client_id,
        credentials.user_agent,
        ['some-scope', 'some-other-scope'])

    store.put(credentials)
    credentials = store.get()

    self.assertNotEquals(None, credentials)
    self.assertEquals('foo', credentials.access_token)

    store.delete()
    credentials = store.get()

    self.assertEquals(None, credentials)

    if os.name == 'posix':
      self.assertEquals('0600', oct(stat.S_IMODE(os.stat(FILENAME).st_mode)))

if __name__ == '__main__':
  unittest.main()
