#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
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
from apiclient.http import HttpMock
from apiclient.http import tunnel_patch
from apiclient.http import HttpMockSequence
from apiclient.errors import HttpError
from apiclient.errors import InvalidJsonError
from apiclient.errors import MediaUploadSizeError
from apiclient.errors import UnacceptableMimeTypeError


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def datafile(filename):
  return os.path.join(DATA_DIR, filename)


class Utilities(unittest.TestCase):
  def test_key2param(self):
    self.assertEqual('max_results', key2param('max-results'))
    self.assertEqual('x007_bond', key2param('007-bond'))


class DiscoveryErrors(unittest.TestCase):

  def test_failed_to_parse_discovery_json(self):
    self.http = HttpMock(datafile('malformed.json'), {'status': '200'})
    try:
      buzz = build('buzz', 'v1', self.http)
      self.fail("should have raised an exception over malformed JSON.")
    except InvalidJsonError:
      pass


class Discovery(unittest.TestCase):

  def test_method_error_checking(self):
    self.http = HttpMock(datafile('buzz.json'), {'status': '200'})
    buzz = build('buzz', 'v1', self.http)

    # Missing required parameters
    try:
      buzz.activities().list()
      self.fail()
    except TypeError, e:
      self.assertTrue('Missing' in str(e))

    # Parameter doesn't match regex
    try:
      buzz.activities().list(scope='@myself', userId='me')
      self.fail()
    except TypeError, e:
      self.assertTrue('not an allowed value' in str(e))

    # Parameter doesn't match regex
    try:
      buzz.activities().list(scope='not@', userId='foo')
      self.fail()
    except TypeError, e:
      self.assertTrue('not an allowed value' in str(e))

    # Unexpected parameter
    try:
      buzz.activities().list(flubber=12)
      self.fail()
    except TypeError, e:
      self.assertTrue('unexpected' in str(e))

  def _check_query_types(self, request):
    parsed = urlparse.urlparse(request.uri)
    q = parse_qs(parsed[4])
    self.assertEqual(q['q'], ['foo'])
    self.assertEqual(q['i'], ['1'])
    self.assertEqual(q['n'], ['1.0'])
    self.assertEqual(q['b'], ['false'])
    self.assertEqual(q['a'], ['[1, 2, 3]'])
    self.assertEqual(q['o'], ['{\'a\': 1}'])
    self.assertEqual(q['e'], ['bar'])

  def test_type_coercion(self):
    http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http)

    request = zoo.query(q="foo", i=1.0, n=1.0, b=0, a=[1,2,3], o={'a':1}, e='bar')
    self._check_query_types(request)
    request = zoo.query(q="foo", i=1, n=1, b=False, a=[1,2,3], o={'a':1}, e='bar')
    self._check_query_types(request)

    request = zoo.query(q="foo", i="1", n="1", b="", a=[1,2,3], o={'a':1}, e='bar')
    self._check_query_types(request)

  def test_optional_stack_query_parameters(self):
    http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http)
    request = zoo.query(trace='html', fields='description')

    parsed = urlparse.urlparse(request.uri)
    q = parse_qs(parsed[4])
    self.assertEqual(q['trace'], ['html'])
    self.assertEqual(q['fields'], ['description'])

  def test_patch(self):
    http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http)
    request = zoo.animals().patch(name='lion', body='{"description": "foo"}')

    self.assertEqual(request.method, 'PATCH')

  def test_tunnel_patch(self):
    http = HttpMockSequence([
      ({'status': '200'}, file(datafile('zoo.json'), 'r').read()),
      ({'status': '200'}, 'echo_request_headers_as_json'),
      ])
    http = tunnel_patch(http)
    zoo = build('zoo', 'v1', http)
    resp = zoo.animals().patch(name='lion', body='{"description": "foo"}').execute()

    self.assertTrue('x-http-method-override' in resp)

  def test_buzz_resources(self):
    self.http = HttpMock(datafile('buzz.json'), {'status': '200'})
    buzz = build('buzz', 'v1', self.http)
    self.assertTrue(getattr(buzz, 'activities'))
    self.assertTrue(getattr(buzz, 'photos'))
    self.assertTrue(getattr(buzz, 'people'))
    self.assertTrue(getattr(buzz, 'groups'))
    self.assertTrue(getattr(buzz, 'comments'))
    self.assertTrue(getattr(buzz, 'related'))

  def test_auth(self):
    self.http = HttpMock(datafile('buzz.json'), {'status': '200'})
    buzz = build('buzz', 'v1', self.http)
    auth = buzz.auth_discovery()
    self.assertTrue('request' in auth)

  def test_full_featured(self):
    # Zoo should exercise all discovery facets
    # and should also have no future.json file.
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', self.http)
    self.assertTrue(getattr(zoo, 'animals'))

    request = zoo.animals().list(name='bat', projection="full")
    parsed = urlparse.urlparse(request.uri)
    q = parse_qs(parsed[4])
    self.assertEqual(q['name'], ['bat'])
    self.assertEqual(q['projection'], ['full'])

  def test_nested_resources(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', self.http)
    self.assertTrue(getattr(zoo, 'animals'))
    request = zoo.my().favorites().list(max_results="5")
    parsed = urlparse.urlparse(request.uri)
    q = parse_qs(parsed[4])
    self.assertEqual(q['max-results'], ['5'])

  def test_methods_with_reserved_names(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', self.http)
    self.assertTrue(getattr(zoo, 'animals'))
    request = zoo.global_().print_().assert_(max_results="5")
    parsed = urlparse.urlparse(request.uri)
    self.assertEqual(parsed[2], '/zoo/global/print/assert')

  def test_top_level_functions(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', self.http)
    self.assertTrue(getattr(zoo, 'query'))
    request = zoo.query(q="foo")
    parsed = urlparse.urlparse(request.uri)
    q = parse_qs(parsed[4])
    self.assertEqual(q['q'], ['foo'])

  def test_simple_media_uploads(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', self.http)
    doc = getattr(zoo.animals().insert, '__doc__')
    self.assertTrue('media_body' in doc)

  def test_simple_media_raise_correct_exceptions(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', self.http)

    try:
      zoo.animals().insert(media_body=datafile('smiley.png'))
      self.fail("should throw exception if media is too large.")
    except MediaUploadSizeError:
      pass

    try:
      zoo.animals().insert(media_body=datafile('small.jpg'))
      self.fail("should throw exception if mimetype is unacceptable.")
    except UnacceptableMimeTypeError:
      pass

  def test_simple_media_good_upload(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', self.http)

    request = zoo.animals().insert(media_body=datafile('small.png'))
    self.assertEquals('image/png', request.headers['content-type'])
    self.assertEquals('PNG', request.body[1:4])

  def test_multipart_media_raise_correct_exceptions(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', self.http)

    try:
      zoo.animals().insert(media_body=datafile('smiley.png'), body={})
      self.fail("should throw exception if media is too large.")
    except MediaUploadSizeError:
      pass

    try:
      zoo.animals().insert(media_body=datafile('small.jpg'), body={})
      self.fail("should throw exception if mimetype is unacceptable.")
    except UnacceptableMimeTypeError:
      pass

  def test_multipart_media_good_upload(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', self.http)

    request = zoo.animals().insert(media_body=datafile('small.png'), body={})
    self.assertTrue(request.headers['content-type'].startswith('multipart/related'))
    self.assertEquals('--==', request.body[0:4])

  def test_media_capable_method_without_media(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', self.http)

    request = zoo.animals().insert(body={})
    self.assertTrue(request.headers['content-type'], 'application/json')

class Next(unittest.TestCase):
  def test_next_for_people_liked(self):
    self.http = HttpMock(datafile('buzz.json'), {'status': '200'})
    buzz = build('buzz', 'v1', self.http)
    people = {'links':
                  {'next':
                   [{'href': 'http://www.googleapis.com/next-link'}]}}
    request = buzz.people().liked_next(people)
    self.assertEqual(request.uri, 'http://www.googleapis.com/next-link')


class DeveloperKey(unittest.TestCase):
  def test_param(self):
    self.http = HttpMock(datafile('buzz.json'), {'status': '200'})
    buzz = build('buzz', 'v1', self.http, developerKey='foobie_bletch')
    activities = {'links':
                  {'next':
                   [{'href': 'http://www.googleapis.com/next-link'}]}}
    request = buzz.activities().list_next(activities)
    parsed = urlparse.urlparse(request.uri)
    q = parse_qs(parsed[4])
    self.assertEqual(q['key'], ['foobie_bletch'])

  def test_next_for_activities_list(self):
    self.http = HttpMock(datafile('buzz.json'), {'status': '200'})
    buzz = build('buzz', 'v1', self.http, developerKey='foobie_bletch')
    activities = {'links':
                  {'next':
                   [{'href': 'http://www.googleapis.com/next-link'}]}}
    request = buzz.activities().list_next(activities)
    self.assertEqual(request.uri,
                     'http://www.googleapis.com/next-link?key=foobie_bletch')


if __name__ == '__main__':
  unittest.main()
