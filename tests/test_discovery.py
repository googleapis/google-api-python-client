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

import httplib2
import os
import unittest
import urlparse
try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

from apiclient.discovery import build, key2param

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

  def test_full_featured(self):
    # Zoo should exercise all discovery facets
    # and should also have no future.json file.
    self.http = HttpMock('zoo.json', {'status': '200'})
    zoo = build('zoo', 'v1', self.http)
    self.assertTrue(getattr(zoo, 'animals'))
    request = zoo.animals().list(name="bat", projection="size")
    parsed = urlparse.urlparse(request.uri)
    q = parse_qs(parsed[4])
    self.assertEqual(q['name'], ['bat'])
    self.assertEqual(q['projection'], ['size'])



class Next(unittest.TestCase):
  def test_next_for_people_liked(self):
    self.http = HttpMock('buzz.json', {'status': '200'})
    buzz = build('buzz', 'v1', self.http)
    people = {'links':
                  {'next':
                   [{'href': 'http://www.googleapis.com/next-link'}]}}
    request = buzz.people().liked_next(people)
    self.assertEqual(request.uri, 'http://www.googleapis.com/next-link')


class DeveloperKey(unittest.TestCase):
  def test_param(self):
    self.http = HttpMock('buzz.json', {'status': '200'})
    buzz = build('buzz', 'v1', self.http, developerKey='foobie_bletch')
    activities = {'links':
                  {'next':
                   [{'href': 'http://www.googleapis.com/next-link'}]}}
    request = buzz.activities().list_next(activities)
    parsed = urlparse.urlparse(request.uri)
    q = parse_qs(parsed[4])
    self.assertEqual(q['key'], ['foobie_bletch'])

  def test_next_for_activities_list(self):
    self.http = HttpMock('buzz.json', {'status': '200'})
    buzz = build('buzz', 'v1', self.http, developerKey='foobie_bletch')
    activities = {'links':
                  {'next':
                   [{'href': 'http://www.googleapis.com/next-link'}]}}
    request = buzz.activities().list_next(activities)
    self.assertEqual(request.uri,
                     'http://www.googleapis.com/next-link?key=foobie_bletch')


if __name__ == '__main__':
  unittest.main()
