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

from apiclient.discovery import build, build_from_document, key2param
from apiclient.errors import HttpError
from apiclient.errors import InvalidJsonError
from apiclient.errors import MediaUploadSizeError
from apiclient.errors import ResumableUploadError
from apiclient.errors import UnacceptableMimeTypeError
from apiclient.http import HttpMock
from apiclient.http import HttpMockSequence
from apiclient.http import MediaFileUpload
from apiclient.http import MediaUploadProgress
from apiclient.http import tunnel_patch


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
      plus = build('plus', 'v1', self.http)
      self.fail("should have raised an exception over malformed JSON.")
    except InvalidJsonError:
      pass


class DiscoveryFromDocument(unittest.TestCase):

  def test_can_build_from_local_document(self):
    discovery = file(datafile('plus.json')).read()
    plus = build_from_document(discovery, base="https://www.googleapis.com/")
    self.assertTrue(plus is not None)

  def test_building_with_base_remembers_base(self):
    discovery = file(datafile('plus.json')).read()

    base = "https://www.example.com/"
    plus = build_from_document(discovery, base=base)
    self.assertEquals(base + "plus/v1/", plus._baseUrl)


class DiscoveryFromHttp(unittest.TestCase):
  def setUp(self):
    self.old_environ = os.environ.copy()

  def tearDown(self):
    os.environ = self.old_environ

  def test_userip_is_added_to_discovery_uri(self):
    # build() will raise an HttpError on a 400, use this to pick the request uri
    # out of the raised exception.
    os.environ['REMOTE_ADDR'] = '10.0.0.1'
    try:
      http = HttpMockSequence([
        ({'status': '400'}, file(datafile('zoo.json'), 'r').read()),
        ])
      zoo = build('zoo', 'v1', http, developerKey='foo',
                  discoveryServiceUrl='http://example.com')
      self.fail('Should have raised an exception.')
    except HttpError, e:
      self.assertEqual(e.uri, 'http://example.com?userIp=10.0.0.1')

  def test_userip_missing_is_not_added_to_discovery_uri(self):
    # build() will raise an HttpError on a 400, use this to pick the request uri
    # out of the raised exception.
    try:
      http = HttpMockSequence([
        ({'status': '400'}, file(datafile('zoo.json'), 'r').read()),
        ])
      zoo = build('zoo', 'v1', http, developerKey=None,
                  discoveryServiceUrl='http://example.com')
      self.fail('Should have raised an exception.')
    except HttpError, e:
      self.assertEqual(e.uri, 'http://example.com')


class Discovery(unittest.TestCase):

  def test_method_error_checking(self):
    self.http = HttpMock(datafile('plus.json'), {'status': '200'})
    plus = build('plus', 'v1', self.http)

    # Missing required parameters
    try:
      plus.activities().list()
      self.fail()
    except TypeError, e:
      self.assertTrue('Missing' in str(e))

    # Parameter doesn't match regex
    try:
      plus.activities().list(collection='not_a_collection_name', userId='me')
      self.fail()
    except TypeError, e:
      self.assertTrue('not an allowed value' in str(e))

    # Unexpected parameter
    try:
      plus.activities().list(flubber=12)
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

    request = zoo.query(
        q="foo", i=1.0, n=1.0, b=0, a=[1,2,3], o={'a':1}, e='bar')
    self._check_query_types(request)
    request = zoo.query(
        q="foo", i=1, n=1, b=False, a=[1,2,3], o={'a':1}, e='bar')
    self._check_query_types(request)

    request = zoo.query(
        q="foo", i="1", n="1", b="", a=[1,2,3], o={'a':1}, e='bar')

    request = zoo.query(
        q="foo", i="1", n="1", b="", a=[1,2,3], o={'a':1}, e='bar', rr=['foo',
                                                                        'bar'])
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
    resp = zoo.animals().patch(
        name='lion', body='{"description": "foo"}').execute()

    self.assertTrue('x-http-method-override' in resp)

  def test_plus_resources(self):
    self.http = HttpMock(datafile('plus.json'), {'status': '200'})
    plus = build('plus', 'v1', self.http)
    self.assertTrue(getattr(plus, 'activities'))
    self.assertTrue(getattr(plus, 'people'))

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

  def test_simple_media_upload_no_max_size_provided(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', self.http)
    request = zoo.animals().crossbreed(media_body=datafile('small.png'))
    self.assertEquals('image/png', request.headers['content-type'])
    self.assertEquals('PNG', request.body[1:4])

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
    self.assertTrue(request.headers['content-type'].startswith(
        'multipart/related'))
    self.assertEquals('--==', request.body[0:4])

  def test_media_capable_method_without_media(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', self.http)

    request = zoo.animals().insert(body={})
    self.assertTrue(request.headers['content-type'], 'application/json')

  def test_resumable_multipart_media_good_upload(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', self.http)

    media_upload = MediaFileUpload(datafile('small.png'), resumable=True)
    request = zoo.animals().insert(media_body=media_upload, body={})
    self.assertTrue(request.headers['content-type'].startswith(
        'multipart/related'))
    self.assertEquals('--==', request.body[0:4])
    self.assertEquals(media_upload, request.resumable)

    self.assertEquals('image/png', request.resumable.mimetype())

    self.assertTrue(len(request.multipart_boundary) > 0)
    self.assertNotEquals(request.body, None)
    self.assertEquals(request.resumable_uri, None)

    http = HttpMockSequence([
      ({'status': '200',
        'location': 'http://upload.example.com'}, ''),
      ({'status': '308',
        'location': 'http://upload.example.com/2',
        'range': '0-12'}, ''),
      ({'status': '308',
        'location': 'http://upload.example.com/3',
        'range': '0-%d' % (request.total_size - 2)}, ''),
      ({'status': '200'}, '{"foo": "bar"}'),
      ])

    status, body = request.next_chunk(http)
    self.assertEquals(None, body)
    self.assertTrue(isinstance(status, MediaUploadProgress))
    self.assertEquals(13, status.resumable_progress)

    # request.body is not None because the server only acknowledged 12 bytes,
    # which is less than the size of the body, so we need to send it again.
    self.assertNotEquals(request.body, None)

    # Two requests should have been made and the resumable_uri should have been
    # updated for each one.
    self.assertEquals(request.resumable_uri, 'http://upload.example.com/2')

    self.assertEquals(media_upload, request.resumable)
    self.assertEquals(13, request.resumable_progress)

    status, body = request.next_chunk(http)
    self.assertEquals(request.resumable_uri, 'http://upload.example.com/3')
    self.assertEquals(request.total_size-1, request.resumable_progress)
    self.assertEquals(request.body, None)

    # Final call to next_chunk should complete the upload.
    status, body = request.next_chunk(http)
    self.assertEquals(body, {"foo": "bar"})
    self.assertEquals(status, None)


  def test_resumable_media_good_upload(self):
    """Not a multipart upload."""
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', self.http)

    media_upload = MediaFileUpload(datafile('small.png'), resumable=True)
    request = zoo.animals().insert(media_body=media_upload, body=None)
    self.assertTrue(request.headers['content-type'].startswith(
        'image/png'))
    self.assertEquals(media_upload, request.resumable)

    self.assertEquals('image/png', request.resumable.mimetype())

    self.assertEquals(request.multipart_boundary, '')
    self.assertEquals(request.body, None)
    self.assertEquals(request.resumable_uri, None)

    http = HttpMockSequence([
      ({'status': '200',
        'location': 'http://upload.example.com'}, ''),
      ({'status': '308',
        'location': 'http://upload.example.com/2',
        'range': '0-12'}, ''),
      ({'status': '308',
        'location': 'http://upload.example.com/3',
        'range': '0-%d' % (request.total_size - 2)}, ''),
      ({'status': '200'}, '{"foo": "bar"}'),
      ])

    status, body = request.next_chunk(http)
    self.assertEquals(None, body)
    self.assertTrue(isinstance(status, MediaUploadProgress))
    self.assertEquals(13, status.resumable_progress)

    # Two requests should have been made and the resumable_uri should have been
    # updated for each one.
    self.assertEquals(request.resumable_uri, 'http://upload.example.com/2')

    self.assertEquals(media_upload, request.resumable)
    self.assertEquals(13, request.resumable_progress)

    status, body = request.next_chunk(http)
    self.assertEquals(request.resumable_uri, 'http://upload.example.com/3')
    self.assertEquals(request.total_size-1, request.resumable_progress)
    self.assertEquals(request.body, None)

    # Final call to next_chunk should complete the upload.
    status, body = request.next_chunk(http)
    self.assertEquals(body, {"foo": "bar"})
    self.assertEquals(status, None)


  def test_resumable_media_good_upload_from_execute(self):
    """Not a multipart upload."""
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', self.http)

    media_upload = MediaFileUpload(datafile('small.png'), resumable=True)
    request = zoo.animals().insert(media_body=media_upload, body=None)

    http = HttpMockSequence([
      ({'status': '200',
        'location': 'http://upload.example.com'}, ''),
      ({'status': '308',
        'location': 'http://upload.example.com/2',
        'range': '0-12'}, ''),
      ({'status': '308',
        'location': 'http://upload.example.com/3',
        'range': '0-%d' % (request.total_size - 2)}, ''),
      ({'status': '200'}, '{"foo": "bar"}'),
      ])

    body = request.execute(http)
    self.assertEquals(body, {"foo": "bar"})

  def test_resumable_media_fail_unknown_response_code_first_request(self):
    """Not a multipart upload."""
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', self.http)

    media_upload = MediaFileUpload(datafile('small.png'), resumable=True)
    request = zoo.animals().insert(media_body=media_upload, body=None)

    http = HttpMockSequence([
      ({'status': '400',
        'location': 'http://upload.example.com'}, ''),
      ])

    self.assertRaises(ResumableUploadError, request.execute, http)

  def test_resumable_media_fail_unknown_response_code_subsequent_request(self):
    """Not a multipart upload."""
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', self.http)

    media_upload = MediaFileUpload(datafile('small.png'), resumable=True)
    request = zoo.animals().insert(media_body=media_upload, body=None)

    http = HttpMockSequence([
      ({'status': '200',
        'location': 'http://upload.example.com'}, ''),
      ({'status': '400'}, ''),
      ])

    self.assertRaises(HttpError, request.execute, http)


class Next(unittest.TestCase):

  def test_next_successful_none_on_no_next_page_token(self):
    self.http = HttpMock(datafile('tasks.json'), {'status': '200'})
    tasks = build('tasks', 'v1', self.http)
    request = tasks.tasklists().list()
    self.assertEqual(None, tasks.tasklists().list_next(request, {}))

  def test_next_successful_with_next_page_token(self):
    self.http = HttpMock(datafile('tasks.json'), {'status': '200'})
    tasks = build('tasks', 'v1', self.http)
    request = tasks.tasklists().list()
    next_request = tasks.tasklists().list_next(
        request, {'nextPageToken': '123abc'})
    parsed = list(urlparse.urlparse(next_request.uri))
    q = parse_qs(parsed[4])
    self.assertEqual(q['pageToken'][0], '123abc')

  def test_next_with_method_with_no_properties(self):
    self.http = HttpMock(datafile('latitude.json'), {'status': '200'})
    service = build('latitude', 'v1', self.http)
    request = service.currentLocation().get()


if __name__ == '__main__':
  unittest.main()
