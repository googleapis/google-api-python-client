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


"""Discovery document tests

Unit tests for objects created from discovery documents.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

from apiclient.discovery import build, key2param
import httplib2
import os
import unittest

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

class HttpMock(object):

  def __init__(self, filename, headers):
    f = file(os.path.join(DATA_DIR, filename), 'r')
    self.data = f.read()
    f.close()
    self.headers = headers

  def request(self, uri, method="GET", body=None, headers=None, redirections=1, connection_type=None):
    return httplib2.Response(self.headers), self.data


class Utilities(unittest.TestCase):
  def test_key2param(self):
    self.assertEqual('max_results', key2param('max-results'))
    self.assertEqual('x007_bond', key2param('007-bond'))


class Discovery(unittest.TestCase):
  def test_method_error_checking(self):
    self.http = HttpMock('buzz.json', {'status': '200'})
    buzz = build('buzz', 'v1', self.http)

    # Missing required parameters
    try:
      buzz.activities().list()
      self.fail()
    except TypeError, e:
      self.assertTrue('Missing' in str(e))

    # Parameter doesn't match regex
    try:
      buzz.activities().list(scope='@self', userId='')
      self.fail()
    except TypeError, e:
      self.assertTrue('does not match' in str(e))

    # Parameter doesn't match regex
    try:
      buzz.activities().list(scope='not@', userId='foo')
      self.fail()
    except TypeError, e:
      self.assertTrue('does not match' in str(e))

    # Unexpected parameter
    try:
      buzz.activities().list(flubber=12)
      self.fail()
    except TypeError, e:
      self.assertTrue('unexpected' in str(e))

  def test_buzz_resources(self):
    self.http = HttpMock('buzz.json', {'status': '200'})
    buzz = build('buzz', 'v1', self.http)
    self.assertTrue(getattr(buzz, 'activities'))
    self.assertTrue(getattr(buzz, 'search'))
    self.assertTrue(getattr(buzz, 'feeds'))
    self.assertTrue(getattr(buzz, 'photos'))
    self.assertTrue(getattr(buzz, 'people'))
    self.assertTrue(getattr(buzz, 'groups'))
    self.assertTrue(getattr(buzz, 'comments'))
    self.assertTrue(getattr(buzz, 'related'))

  def test_auth(self):
    self.http = HttpMock('buzz.json', {'status': '200'})
    buzz = build('buzz', 'v1', self.http)
    auth = buzz.auth_discovery()
    self.assertTrue('request' in auth)


class Next(unittest.TestCase):
  def test_next(self):
    self.http = HttpMock('buzz.json', {'status': '200'})
    buzz = build('buzz', 'v1', self.http)
    activities = {'links':
                  {'next':
                   [{'href': 'http://www.googleapis.com/next-link'}]}}
    request = buzz.activities().list_next(activities)
    self.assertEqual(request.uri, 'http://www.googleapis.com/next-link')


if __name__ == '__main__':
  unittest.main()
