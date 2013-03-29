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

import copy
import datetime
import httplib2
import os
import pickle
import sys
import unittest
import urlparse
import StringIO


try:
  from urlparse import parse_qs
except ImportError:
  from cgi import parse_qs


from apiclient.discovery import _fix_up_media_upload
from apiclient.discovery import _fix_up_method_description
from apiclient.discovery import _fix_up_parameters
from apiclient.discovery import build
from apiclient.discovery import build_from_document
from apiclient.discovery import DISCOVERY_URI
from apiclient.discovery import key2param
from apiclient.discovery import MEDIA_BODY_PARAMETER_DEFAULT_VALUE
from apiclient.discovery import ResourceMethodParameters
from apiclient.discovery import STACK_QUERY_PARAMETERS
from apiclient.discovery import STACK_QUERY_PARAMETER_DEFAULT_VALUE
from apiclient.errors import HttpError
from apiclient.errors import InvalidJsonError
from apiclient.errors import MediaUploadSizeError
from apiclient.errors import ResumableUploadError
from apiclient.errors import UnacceptableMimeTypeError
from apiclient.http import HttpMock
from apiclient.http import HttpMockSequence
from apiclient.http import MediaFileUpload
from apiclient.http import MediaIoBaseUpload
from apiclient.http import MediaUpload
from apiclient.http import MediaUploadProgress
from apiclient.http import tunnel_patch
from oauth2client import GOOGLE_TOKEN_URI
from oauth2client import util
from oauth2client.anyjson import simplejson
from oauth2client.client import OAuth2Credentials

import uritemplate


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

util.positional_parameters_enforcement = util.POSITIONAL_EXCEPTION


def assertUrisEqual(testcase, expected, actual):
  """Test that URIs are the same, up to reordering of query parameters."""
  expected = urlparse.urlparse(expected)
  actual = urlparse.urlparse(actual)
  testcase.assertEqual(expected.scheme, actual.scheme)
  testcase.assertEqual(expected.netloc, actual.netloc)
  testcase.assertEqual(expected.path, actual.path)
  testcase.assertEqual(expected.params, actual.params)
  testcase.assertEqual(expected.fragment, actual.fragment)
  expected_query = parse_qs(expected.query)
  actual_query = parse_qs(actual.query)
  for name in expected_query.keys():
    testcase.assertEqual(expected_query[name], actual_query[name])
  for name in actual_query.keys():
    testcase.assertEqual(expected_query[name], actual_query[name])


def datafile(filename):
  return os.path.join(DATA_DIR, filename)


class SetupHttplib2(unittest.TestCase):

  def test_retries(self):
    # Merely loading apiclient.discovery should set the RETRIES to 1.
    self.assertEqual(1, httplib2.RETRIES)


class Utilities(unittest.TestCase):

  def setUp(self):
    with open(datafile('zoo.json'), 'r') as fh:
      self.zoo_root_desc = simplejson.loads(fh.read())
    self.zoo_get_method_desc = self.zoo_root_desc['methods']['query']
    self.zoo_animals_resource = self.zoo_root_desc['resources']['animals']
    self.zoo_insert_method_desc = self.zoo_animals_resource['methods']['insert']

  def test_key2param(self):
    self.assertEqual('max_results', key2param('max-results'))
    self.assertEqual('x007_bond', key2param('007-bond'))

  def _base_fix_up_parameters_test(self, method_desc, http_method, root_desc):
    self.assertEqual(method_desc['httpMethod'], http_method)

    method_desc_copy = copy.deepcopy(method_desc)
    self.assertEqual(method_desc, method_desc_copy)

    parameters = _fix_up_parameters(method_desc_copy, root_desc, http_method)

    self.assertNotEqual(method_desc, method_desc_copy)

    for param_name in STACK_QUERY_PARAMETERS:
      self.assertEqual(STACK_QUERY_PARAMETER_DEFAULT_VALUE,
                       parameters[param_name])

    for param_name, value in root_desc.get('parameters', {}).iteritems():
      self.assertEqual(value, parameters[param_name])

    return parameters

  def test_fix_up_parameters_get(self):
    parameters = self._base_fix_up_parameters_test(self.zoo_get_method_desc,
                                                   'GET', self.zoo_root_desc)
    # Since http_method is 'GET'
    self.assertFalse(parameters.has_key('body'))

  def test_fix_up_parameters_insert(self):
    parameters = self._base_fix_up_parameters_test(self.zoo_insert_method_desc,
                                                   'POST', self.zoo_root_desc)
    body = {
        'description': 'The request body.',
        'type': 'object',
        'required': True,
        '$ref': 'Animal',
    }
    self.assertEqual(parameters['body'], body)

  def test_fix_up_parameters_check_body(self):
    dummy_root_desc = {}
    no_payload_http_method = 'DELETE'
    with_payload_http_method = 'PUT'

    invalid_method_desc = {'response': 'Who cares'}
    valid_method_desc = {'request': {'key1': 'value1', 'key2': 'value2'}}

    parameters = _fix_up_parameters(invalid_method_desc, dummy_root_desc,
                                    no_payload_http_method)
    self.assertFalse(parameters.has_key('body'))

    parameters = _fix_up_parameters(valid_method_desc, dummy_root_desc,
                                    no_payload_http_method)
    self.assertFalse(parameters.has_key('body'))

    parameters = _fix_up_parameters(invalid_method_desc, dummy_root_desc,
                                    with_payload_http_method)
    self.assertFalse(parameters.has_key('body'))

    parameters = _fix_up_parameters(valid_method_desc, dummy_root_desc,
                                    with_payload_http_method)
    body = {
        'description': 'The request body.',
        'type': 'object',
        'required': True,
        'key1': 'value1',
        'key2': 'value2',
    }
    self.assertEqual(parameters['body'], body)

  def _base_fix_up_method_description_test(
      self, method_desc, initial_parameters, final_parameters,
      final_accept, final_max_size, final_media_path_url):
    fake_root_desc = {'rootUrl': 'http://root/',
                      'servicePath': 'fake/'}
    fake_path_url = 'fake-path/'

    accept, max_size, media_path_url = _fix_up_media_upload(
        method_desc, fake_root_desc, fake_path_url, initial_parameters)
    self.assertEqual(accept, final_accept)
    self.assertEqual(max_size, final_max_size)
    self.assertEqual(media_path_url, final_media_path_url)
    self.assertEqual(initial_parameters, final_parameters)

  def test_fix_up_media_upload_no_initial_invalid(self):
    invalid_method_desc = {'response': 'Who cares'}
    self._base_fix_up_method_description_test(invalid_method_desc, {}, {},
                                              [], 0, None)

  def test_fix_up_media_upload_no_initial_valid_minimal(self):
    valid_method_desc = {'mediaUpload': {'accept': []}}
    final_parameters = {'media_body': MEDIA_BODY_PARAMETER_DEFAULT_VALUE}
    self._base_fix_up_method_description_test(
        valid_method_desc, {}, final_parameters, [], 0,
        'http://root/upload/fake/fake-path/')

  def test_fix_up_media_upload_no_initial_valid_full(self):
    valid_method_desc = {'mediaUpload': {'accept': ['*/*'], 'maxSize': '10GB'}}
    final_parameters = {'media_body': MEDIA_BODY_PARAMETER_DEFAULT_VALUE}
    ten_gb = 10 * 2**30
    self._base_fix_up_method_description_test(
        valid_method_desc, {}, final_parameters, ['*/*'],
        ten_gb, 'http://root/upload/fake/fake-path/')

  def test_fix_up_media_upload_with_initial_invalid(self):
    invalid_method_desc = {'response': 'Who cares'}
    initial_parameters = {'body': {}}
    self._base_fix_up_method_description_test(
        invalid_method_desc, initial_parameters,
        initial_parameters, [], 0, None)

  def test_fix_up_media_upload_with_initial_valid_minimal(self):
    valid_method_desc = {'mediaUpload': {'accept': []}}
    initial_parameters = {'body': {}}
    final_parameters = {'body': {'required': False},
                        'media_body': MEDIA_BODY_PARAMETER_DEFAULT_VALUE}
    self._base_fix_up_method_description_test(
        valid_method_desc, initial_parameters, final_parameters, [], 0,
        'http://root/upload/fake/fake-path/')

  def test_fix_up_media_upload_with_initial_valid_full(self):
    valid_method_desc = {'mediaUpload': {'accept': ['*/*'], 'maxSize': '10GB'}}
    initial_parameters = {'body': {}}
    final_parameters = {'body': {'required': False},
                        'media_body': MEDIA_BODY_PARAMETER_DEFAULT_VALUE}
    ten_gb = 10 * 2**30
    self._base_fix_up_method_description_test(
        valid_method_desc, initial_parameters, final_parameters, ['*/*'],
        ten_gb, 'http://root/upload/fake/fake-path/')

  def test_fix_up_method_description_get(self):
    result = _fix_up_method_description(self.zoo_get_method_desc,
                                        self.zoo_root_desc)
    path_url = 'query'
    http_method = 'GET'
    method_id = 'bigquery.query'
    accept = []
    max_size = 0L
    media_path_url = None
    self.assertEqual(result, (path_url, http_method, method_id, accept,
                              max_size, media_path_url))

  def test_fix_up_method_description_insert(self):
    result = _fix_up_method_description(self.zoo_insert_method_desc,
                                        self.zoo_root_desc)
    path_url = 'animals'
    http_method = 'POST'
    method_id = 'zoo.animals.insert'
    accept = ['image/png']
    max_size = 1024L
    media_path_url = 'https://www.googleapis.com/upload/zoo/v1/animals'
    self.assertEqual(result, (path_url, http_method, method_id, accept,
                              max_size, media_path_url))

  def test_ResourceMethodParameters_zoo_get(self):
    parameters = ResourceMethodParameters(self.zoo_get_method_desc)

    param_types = {'a': 'any',
                   'b': 'boolean',
                   'e': 'string',
                   'er': 'string',
                   'i': 'integer',
                   'n': 'number',
                   'o': 'object',
                   'q': 'string',
                   'rr': 'string'}
    keys = param_types.keys()
    self.assertEqual(parameters.argmap, dict((key, key) for key in keys))
    self.assertEqual(parameters.required_params, [])
    self.assertEqual(sorted(parameters.repeated_params), ['er', 'rr'])
    self.assertEqual(parameters.pattern_params, {'rr': '[a-z]+'})
    self.assertEqual(sorted(parameters.query_params),
                     ['a', 'b', 'e', 'er', 'i', 'n', 'o', 'q', 'rr'])
    self.assertEqual(parameters.path_params, set())
    self.assertEqual(parameters.param_types, param_types)
    enum_params = {'e': ['foo', 'bar'],
                   'er': ['one', 'two', 'three']}
    self.assertEqual(parameters.enum_params, enum_params)

  def test_ResourceMethodParameters_zoo_animals_patch(self):
    method_desc = self.zoo_animals_resource['methods']['patch']
    parameters = ResourceMethodParameters(method_desc)

    param_types = {'name': 'string'}
    keys = param_types.keys()
    self.assertEqual(parameters.argmap, dict((key, key) for key in keys))
    self.assertEqual(parameters.required_params, ['name'])
    self.assertEqual(parameters.repeated_params, [])
    self.assertEqual(parameters.pattern_params, {})
    self.assertEqual(parameters.query_params, [])
    self.assertEqual(parameters.path_params, set(['name']))
    self.assertEqual(parameters.param_types, param_types)
    self.assertEqual(parameters.enum_params, {})


class DiscoveryErrors(unittest.TestCase):

  def test_tests_should_be_run_with_strict_positional_enforcement(self):
    try:
      plus = build('plus', 'v1', None)
      self.fail("should have raised a TypeError exception over missing http=.")
    except TypeError:
      pass

  def test_failed_to_parse_discovery_json(self):
    self.http = HttpMock(datafile('malformed.json'), {'status': '200'})
    try:
      plus = build('plus', 'v1', http=self.http)
      self.fail("should have raised an exception over malformed JSON.")
    except InvalidJsonError:
      pass


class DiscoveryFromDocument(unittest.TestCase):

  def test_can_build_from_local_document(self):
    discovery = open(datafile('plus.json')).read()
    plus = build_from_document(discovery, base="https://www.googleapis.com/")
    self.assertTrue(plus is not None)
    self.assertTrue(hasattr(plus, 'activities'))

  def test_can_build_from_local_deserialized_document(self):
    discovery = open(datafile('plus.json')).read()
    discovery = simplejson.loads(discovery)
    plus = build_from_document(discovery, base="https://www.googleapis.com/")
    self.assertTrue(plus is not None)
    self.assertTrue(hasattr(plus, 'activities'))

  def test_building_with_base_remembers_base(self):
    discovery = open(datafile('plus.json')).read()

    base = "https://www.example.com/"
    plus = build_from_document(discovery, base=base)
    self.assertEquals("https://www.googleapis.com/plus/v1/", plus._baseUrl)


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
        ({'status': '400'}, open(datafile('zoo.json'), 'rb').read()),
        ])
      zoo = build('zoo', 'v1', http=http, developerKey='foo',
                  discoveryServiceUrl='http://example.com')
      self.fail('Should have raised an exception.')
    except HttpError, e:
      self.assertEqual(e.uri, 'http://example.com?userIp=10.0.0.1')

  def test_userip_missing_is_not_added_to_discovery_uri(self):
    # build() will raise an HttpError on a 400, use this to pick the request uri
    # out of the raised exception.
    try:
      http = HttpMockSequence([
        ({'status': '400'}, open(datafile('zoo.json'), 'rb').read()),
        ])
      zoo = build('zoo', 'v1', http=http, developerKey=None,
                  discoveryServiceUrl='http://example.com')
      self.fail('Should have raised an exception.')
    except HttpError, e:
      self.assertEqual(e.uri, 'http://example.com')


class Discovery(unittest.TestCase):

  def test_method_error_checking(self):
    self.http = HttpMock(datafile('plus.json'), {'status': '200'})
    plus = build('plus', 'v1', http=self.http)

    # Missing required parameters
    try:
      plus.activities().list()
      self.fail()
    except TypeError, e:
      self.assertTrue('Missing' in str(e))

    # Missing required parameters even if supplied as None.
    try:
      plus.activities().list(collection=None, userId=None)
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
    zoo = build('zoo', 'v1', http=http)

    request = zoo.query(
        q="foo", i=1.0, n=1.0, b=0, a=[1,2,3], o={'a':1}, e='bar')
    self._check_query_types(request)
    request = zoo.query(
        q="foo", i=1, n=1, b=False, a=[1,2,3], o={'a':1}, e='bar')
    self._check_query_types(request)

    request = zoo.query(
        q="foo", i="1", n="1", b="", a=[1,2,3], o={'a':1}, e='bar', er='two')

    request = zoo.query(
        q="foo", i="1", n="1", b="", a=[1,2,3], o={'a':1}, e='bar',
        er=['one', 'three'], rr=['foo', 'bar'])
    self._check_query_types(request)

    # Five is right out.
    self.assertRaises(TypeError, zoo.query, er=['one', 'five'])

  def test_optional_stack_query_parameters(self):
    http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=http)
    request = zoo.query(trace='html', fields='description')

    parsed = urlparse.urlparse(request.uri)
    q = parse_qs(parsed[4])
    self.assertEqual(q['trace'], ['html'])
    self.assertEqual(q['fields'], ['description'])

  def test_string_params_value_of_none_get_dropped(self):
    http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=http)
    request = zoo.query(trace=None, fields='description')

    parsed = urlparse.urlparse(request.uri)
    q = parse_qs(parsed[4])
    self.assertFalse('trace' in q)

  def test_model_added_query_parameters(self):
    http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=http)
    request = zoo.animals().get(name='Lion')

    parsed = urlparse.urlparse(request.uri)
    q = parse_qs(parsed[4])
    self.assertEqual(q['alt'], ['json'])
    self.assertEqual(request.headers['accept'], 'application/json')

  def test_fallback_to_raw_model(self):
    http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=http)
    request = zoo.animals().getmedia(name='Lion')

    parsed = urlparse.urlparse(request.uri)
    q = parse_qs(parsed[4])
    self.assertTrue('alt' not in q)
    self.assertEqual(request.headers['accept'], '*/*')

  def test_patch(self):
    http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=http)
    request = zoo.animals().patch(name='lion', body='{"description": "foo"}')

    self.assertEqual(request.method, 'PATCH')

  def test_tunnel_patch(self):
    http = HttpMockSequence([
      ({'status': '200'}, open(datafile('zoo.json'), 'rb').read()),
      ({'status': '200'}, 'echo_request_headers_as_json'),
      ])
    http = tunnel_patch(http)
    zoo = build('zoo', 'v1', http=http)
    resp = zoo.animals().patch(
        name='lion', body='{"description": "foo"}').execute()

    self.assertTrue('x-http-method-override' in resp)

  def test_plus_resources(self):
    self.http = HttpMock(datafile('plus.json'), {'status': '200'})
    plus = build('plus', 'v1', http=self.http)
    self.assertTrue(getattr(plus, 'activities'))
    self.assertTrue(getattr(plus, 'people'))

  def test_full_featured(self):
    # Zoo should exercise all discovery facets
    # and should also have no future.json file.
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=self.http)
    self.assertTrue(getattr(zoo, 'animals'))

    request = zoo.animals().list(name='bat', projection="full")
    parsed = urlparse.urlparse(request.uri)
    q = parse_qs(parsed[4])
    self.assertEqual(q['name'], ['bat'])
    self.assertEqual(q['projection'], ['full'])

  def test_nested_resources(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=self.http)
    self.assertTrue(getattr(zoo, 'animals'))
    request = zoo.my().favorites().list(max_results="5")
    parsed = urlparse.urlparse(request.uri)
    q = parse_qs(parsed[4])
    self.assertEqual(q['max-results'], ['5'])

  def test_methods_with_reserved_names(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=self.http)
    self.assertTrue(getattr(zoo, 'animals'))
    request = zoo.global_().print_().assert_(max_results="5")
    parsed = urlparse.urlparse(request.uri)
    self.assertEqual(parsed[2], '/zoo/v1/global/print/assert')

  def test_top_level_functions(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=self.http)
    self.assertTrue(getattr(zoo, 'query'))
    request = zoo.query(q="foo")
    parsed = urlparse.urlparse(request.uri)
    q = parse_qs(parsed[4])
    self.assertEqual(q['q'], ['foo'])

  def test_simple_media_uploads(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=self.http)
    doc = getattr(zoo.animals().insert, '__doc__')
    self.assertTrue('media_body' in doc)

  def test_simple_media_upload_no_max_size_provided(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=self.http)
    request = zoo.animals().crossbreed(media_body=datafile('small.png'))
    self.assertEquals('image/png', request.headers['content-type'])
    self.assertEquals('PNG', request.body[1:4])

  def test_simple_media_raise_correct_exceptions(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=self.http)

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
    zoo = build('zoo', 'v1', http=self.http)

    request = zoo.animals().insert(media_body=datafile('small.png'))
    self.assertEquals('image/png', request.headers['content-type'])
    self.assertEquals('PNG', request.body[1:4])
    assertUrisEqual(self,
        'https://www.googleapis.com/upload/zoo/v1/animals?uploadType=media&alt=json',
        request.uri)

  def test_multipart_media_raise_correct_exceptions(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=self.http)

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
    zoo = build('zoo', 'v1', http=self.http)

    request = zoo.animals().insert(media_body=datafile('small.png'), body={})
    self.assertTrue(request.headers['content-type'].startswith(
        'multipart/related'))
    self.assertEquals('--==', request.body[0:4])
    assertUrisEqual(self,
        'https://www.googleapis.com/upload/zoo/v1/animals?uploadType=multipart&alt=json',
        request.uri)

  def test_media_capable_method_without_media(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=self.http)

    request = zoo.animals().insert(body={})
    self.assertTrue(request.headers['content-type'], 'application/json')

  def test_resumable_multipart_media_good_upload(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=self.http)

    media_upload = MediaFileUpload(datafile('small.png'), resumable=True)
    request = zoo.animals().insert(media_body=media_upload, body={})
    self.assertTrue(request.headers['content-type'].startswith(
        'application/json'))
    self.assertEquals('{"data": {}}', request.body)
    self.assertEquals(media_upload, request.resumable)

    self.assertEquals('image/png', request.resumable.mimetype())

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
        'range': '0-%d' % (media_upload.size() - 2)}, ''),
      ({'status': '200'}, '{"foo": "bar"}'),
      ])

    status, body = request.next_chunk(http=http)
    self.assertEquals(None, body)
    self.assertTrue(isinstance(status, MediaUploadProgress))
    self.assertEquals(13, status.resumable_progress)

    # Two requests should have been made and the resumable_uri should have been
    # updated for each one.
    self.assertEquals(request.resumable_uri, 'http://upload.example.com/2')

    self.assertEquals(media_upload, request.resumable)
    self.assertEquals(13, request.resumable_progress)

    status, body = request.next_chunk(http=http)
    self.assertEquals(request.resumable_uri, 'http://upload.example.com/3')
    self.assertEquals(media_upload.size()-1, request.resumable_progress)
    self.assertEquals('{"data": {}}', request.body)

    # Final call to next_chunk should complete the upload.
    status, body = request.next_chunk(http=http)
    self.assertEquals(body, {"foo": "bar"})
    self.assertEquals(status, None)


  def test_resumable_media_good_upload(self):
    """Not a multipart upload."""
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=self.http)

    media_upload = MediaFileUpload(datafile('small.png'), resumable=True)
    request = zoo.animals().insert(media_body=media_upload, body=None)
    self.assertEquals(media_upload, request.resumable)

    self.assertEquals('image/png', request.resumable.mimetype())

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
        'range': '0-%d' % (media_upload.size() - 2)}, ''),
      ({'status': '200'}, '{"foo": "bar"}'),
      ])

    status, body = request.next_chunk(http=http)
    self.assertEquals(None, body)
    self.assertTrue(isinstance(status, MediaUploadProgress))
    self.assertEquals(13, status.resumable_progress)

    # Two requests should have been made and the resumable_uri should have been
    # updated for each one.
    self.assertEquals(request.resumable_uri, 'http://upload.example.com/2')

    self.assertEquals(media_upload, request.resumable)
    self.assertEquals(13, request.resumable_progress)

    status, body = request.next_chunk(http=http)
    self.assertEquals(request.resumable_uri, 'http://upload.example.com/3')
    self.assertEquals(media_upload.size()-1, request.resumable_progress)
    self.assertEquals(request.body, None)

    # Final call to next_chunk should complete the upload.
    status, body = request.next_chunk(http=http)
    self.assertEquals(body, {"foo": "bar"})
    self.assertEquals(status, None)

  def test_resumable_media_good_upload_from_execute(self):
    """Not a multipart upload."""
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=self.http)

    media_upload = MediaFileUpload(datafile('small.png'), resumable=True)
    request = zoo.animals().insert(media_body=media_upload, body=None)
    assertUrisEqual(self,
        'https://www.googleapis.com/upload/zoo/v1/animals?uploadType=resumable&alt=json',
        request.uri)

    http = HttpMockSequence([
      ({'status': '200',
        'location': 'http://upload.example.com'}, ''),
      ({'status': '308',
        'location': 'http://upload.example.com/2',
        'range': '0-12'}, ''),
      ({'status': '308',
        'location': 'http://upload.example.com/3',
        'range': '0-%d' % media_upload.size()}, ''),
      ({'status': '200'}, '{"foo": "bar"}'),
      ])

    body = request.execute(http=http)
    self.assertEquals(body, {"foo": "bar"})

  def test_resumable_media_fail_unknown_response_code_first_request(self):
    """Not a multipart upload."""
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=self.http)

    media_upload = MediaFileUpload(datafile('small.png'), resumable=True)
    request = zoo.animals().insert(media_body=media_upload, body=None)

    http = HttpMockSequence([
      ({'status': '400',
        'location': 'http://upload.example.com'}, ''),
      ])

    try:
      request.execute(http=http)
      self.fail('Should have raised ResumableUploadError.')
    except ResumableUploadError, e:
      self.assertEqual(400, e.resp.status)

  def test_resumable_media_fail_unknown_response_code_subsequent_request(self):
    """Not a multipart upload."""
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=self.http)

    media_upload = MediaFileUpload(datafile('small.png'), resumable=True)
    request = zoo.animals().insert(media_body=media_upload, body=None)

    http = HttpMockSequence([
      ({'status': '200',
        'location': 'http://upload.example.com'}, ''),
      ({'status': '400'}, ''),
      ])

    self.assertRaises(HttpError, request.execute, http=http)
    self.assertTrue(request._in_error_state)

    http = HttpMockSequence([
      ({'status': '308',
        'range': '0-5'}, ''),
      ({'status': '308',
        'range': '0-6'}, ''),
      ])

    status, body = request.next_chunk(http=http)
    self.assertEquals(status.resumable_progress, 7,
      'Should have first checked length and then tried to PUT more.')
    self.assertFalse(request._in_error_state)

    # Put it back in an error state.
    http = HttpMockSequence([
      ({'status': '400'}, ''),
      ])
    self.assertRaises(HttpError, request.execute, http=http)
    self.assertTrue(request._in_error_state)

    # Pretend the last request that 400'd actually succeeded.
    http = HttpMockSequence([
      ({'status': '200'}, '{"foo": "bar"}'),
      ])
    status, body = request.next_chunk(http=http)
    self.assertEqual(body, {'foo': 'bar'})

  def test_media_io_base_stream_unlimited_chunksize_resume(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=self.http)

    try:
      import io

      # Set up a seekable stream and try to upload in single chunk.
      fd = io.BytesIO('01234"56789"')
      media_upload = MediaIoBaseUpload(
          fd=fd, mimetype='text/plain', chunksize=-1, resumable=True)

      request = zoo.animals().insert(media_body=media_upload, body=None)

      # The single chunk fails, restart at the right point.
      http = HttpMockSequence([
        ({'status': '200',
          'location': 'http://upload.example.com'}, ''),
        ({'status': '308',
          'location': 'http://upload.example.com/2',
          'range': '0-4'}, ''),
        ({'status': '200'}, 'echo_request_body'),
        ])

      body = request.execute(http=http)
      self.assertEqual('56789', body)

    except ImportError:
      pass


  def test_media_io_base_stream_chunksize_resume(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=self.http)

    try:
      import io

      # Set up a seekable stream and try to upload in chunks.
      fd = io.BytesIO('0123456789')
      media_upload = MediaIoBaseUpload(
          fd=fd, mimetype='text/plain', chunksize=5, resumable=True)

      request = zoo.animals().insert(media_body=media_upload, body=None)

      # The single chunk fails, pull the content sent out of the exception.
      http = HttpMockSequence([
        ({'status': '200',
          'location': 'http://upload.example.com'}, ''),
        ({'status': '400'}, 'echo_request_body'),
        ])

      try:
        body = request.execute(http=http)
      except HttpError, e:
        self.assertEqual('01234', e.content)

    except ImportError:
      pass


  def test_resumable_media_handle_uploads_of_unknown_size(self):
    http = HttpMockSequence([
      ({'status': '200',
        'location': 'http://upload.example.com'}, ''),
      ({'status': '200'}, 'echo_request_headers_as_json'),
      ])

    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=self.http)

    # Create an upload that doesn't know the full size of the media.
    class IoBaseUnknownLength(MediaUpload):
      def chunksize(self):
        return 10

      def mimetype(self):
        return 'image/png'

      def size(self):
        return None

      def resumable(self):
        return True

      def getbytes(self, begin, length):
        return '0123456789'

    upload = IoBaseUnknownLength()

    request = zoo.animals().insert(media_body=upload, body=None)
    status, body = request.next_chunk(http=http)
    self.assertEqual(body, {
        'Content-Range': 'bytes 0-9/*',
        'Content-Length': '10',
        })

  def test_resumable_media_no_streaming_on_unsupported_platforms(self):
    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=self.http)

    class IoBaseHasStream(MediaUpload):
      def chunksize(self):
        return 10

      def mimetype(self):
        return 'image/png'

      def size(self):
        return None

      def resumable(self):
        return True

      def getbytes(self, begin, length):
        return '0123456789'

      def has_stream(self):
        return True

      def stream(self):
        raise NotImplementedError()

    upload = IoBaseHasStream()

    orig_version = sys.version_info
    sys.version_info = (2, 5, 5, 'final', 0)

    request = zoo.animals().insert(media_body=upload, body=None)

    http = HttpMockSequence([
      ({'status': '200',
        'location': 'http://upload.example.com'}, ''),
      ({'status': '200'}, 'echo_request_headers_as_json'),
      ])

    # This should not raise an exception because stream() shouldn't be called.
    status, body = request.next_chunk(http=http)
    self.assertEqual(body, {
        'Content-Range': 'bytes 0-9/*',
        'Content-Length': '10'
        })

    sys.version_info = (2, 6, 5, 'final', 0)

    request = zoo.animals().insert(media_body=upload, body=None)

    # This should raise an exception because stream() will be called.
    http = HttpMockSequence([
      ({'status': '200',
        'location': 'http://upload.example.com'}, ''),
      ({'status': '200'}, 'echo_request_headers_as_json'),
      ])

    self.assertRaises(NotImplementedError, request.next_chunk, http=http)

    sys.version_info = orig_version

  def test_resumable_media_handle_uploads_of_unknown_size_eof(self):
    http = HttpMockSequence([
      ({'status': '200',
        'location': 'http://upload.example.com'}, ''),
      ({'status': '200'}, 'echo_request_headers_as_json'),
      ])

    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=self.http)

    fd = StringIO.StringIO('data goes here')

    # Create an upload that doesn't know the full size of the media.
    upload = MediaIoBaseUpload(
        fd=fd, mimetype='image/png', chunksize=15, resumable=True)

    request = zoo.animals().insert(media_body=upload, body=None)
    status, body = request.next_chunk(http=http)
    self.assertEqual(body, {
        'Content-Range': 'bytes 0-13/14',
        'Content-Length': '14',
        })

  def test_resumable_media_handle_resume_of_upload_of_unknown_size(self):
    http = HttpMockSequence([
      ({'status': '200',
        'location': 'http://upload.example.com'}, ''),
      ({'status': '400'}, ''),
      ])

    self.http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=self.http)

    # Create an upload that doesn't know the full size of the media.
    fd = StringIO.StringIO('data goes here')

    upload = MediaIoBaseUpload(
        fd=fd, mimetype='image/png', chunksize=500, resumable=True)

    request = zoo.animals().insert(media_body=upload, body=None)

    # Put it in an error state.
    self.assertRaises(HttpError, request.next_chunk, http=http)

    http = HttpMockSequence([
      ({'status': '400',
        'range': '0-5'}, 'echo_request_headers_as_json'),
      ])
    try:
      # Should resume the upload by first querying the status of the upload.
      request.next_chunk(http=http)
    except HttpError, e:
      expected = {
          'Content-Range': 'bytes */14',
          'content-length': '0'
          }
      self.assertEqual(expected, simplejson.loads(e.content),
        'Should send an empty body when requesting the current upload status.')

  def test_pickle(self):
    sorted_resource_keys = ['_baseUrl',
                            '_developerKey',
                            '_dynamic_attrs',
                            '_http',
                            '_model',
                            '_requestBuilder',
                            '_resourceDesc',
                            '_rootDesc',
                            '_schema',
                            'animals',
                            'global_',
                            'load',
                            'loadNoTemplate',
                            'my',
                            'query',
                            'scopedAnimals']

    http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=http)
    self.assertEqual(sorted(zoo.__dict__.keys()), sorted_resource_keys)

    pickled_zoo = pickle.dumps(zoo)
    new_zoo = pickle.loads(pickled_zoo)
    self.assertEqual(sorted(new_zoo.__dict__.keys()), sorted_resource_keys)
    self.assertTrue(hasattr(new_zoo, 'animals'))
    self.assertTrue(callable(new_zoo.animals))
    self.assertTrue(hasattr(new_zoo, 'global_'))
    self.assertTrue(callable(new_zoo.global_))
    self.assertTrue(hasattr(new_zoo, 'load'))
    self.assertTrue(callable(new_zoo.load))
    self.assertTrue(hasattr(new_zoo, 'loadNoTemplate'))
    self.assertTrue(callable(new_zoo.loadNoTemplate))
    self.assertTrue(hasattr(new_zoo, 'my'))
    self.assertTrue(callable(new_zoo.my))
    self.assertTrue(hasattr(new_zoo, 'query'))
    self.assertTrue(callable(new_zoo.query))
    self.assertTrue(hasattr(new_zoo, 'scopedAnimals'))
    self.assertTrue(callable(new_zoo.scopedAnimals))

    self.assertEqual(sorted(zoo._dynamic_attrs), sorted(new_zoo._dynamic_attrs))
    self.assertEqual(zoo._baseUrl, new_zoo._baseUrl)
    self.assertEqual(zoo._developerKey, new_zoo._developerKey)
    self.assertEqual(zoo._requestBuilder, new_zoo._requestBuilder)
    self.assertEqual(zoo._resourceDesc, new_zoo._resourceDesc)
    self.assertEqual(zoo._rootDesc, new_zoo._rootDesc)
    # _http, _model and _schema won't be equal since we will get new
    # instances upon un-pickling

  def _dummy_zoo_request(self):
    with open(os.path.join(DATA_DIR, 'zoo.json'), 'rU') as fh:
      zoo_contents = fh.read()

    zoo_uri = uritemplate.expand(DISCOVERY_URI,
                                 {'api': 'zoo', 'apiVersion': 'v1'})
    if 'REMOTE_ADDR' in os.environ:
        zoo_uri = util._add_query_parameter(zoo_uri, 'userIp',
                                            os.environ['REMOTE_ADDR'])

    http = httplib2.Http()
    original_request = http.request
    def wrapped_request(uri, method='GET', *args, **kwargs):
        if uri == zoo_uri:
          return httplib2.Response({'status': '200'}), zoo_contents
        return original_request(uri, method=method, *args, **kwargs)
    http.request = wrapped_request
    return http

  def _dummy_token(self):
    access_token = 'foo'
    client_id = 'some_client_id'
    client_secret = 'cOuDdkfjxxnv+'
    refresh_token = '1/0/a.df219fjls0'
    token_expiry = datetime.datetime.utcnow()
    user_agent = 'refresh_checker/1.0'
    return OAuth2Credentials(
        access_token, client_id, client_secret,
        refresh_token, token_expiry, GOOGLE_TOKEN_URI,
        user_agent)

  def test_pickle_with_credentials(self):
    credentials = self._dummy_token()
    http = self._dummy_zoo_request()
    http = credentials.authorize(http)
    self.assertTrue(hasattr(http.request, 'credentials'))

    zoo = build('zoo', 'v1', http=http)
    pickled_zoo = pickle.dumps(zoo)
    new_zoo = pickle.loads(pickled_zoo)
    self.assertEqual(sorted(zoo.__dict__.keys()),
                     sorted(new_zoo.__dict__.keys()))
    new_http = new_zoo._http
    self.assertFalse(hasattr(new_http.request, 'credentials'))


class Next(unittest.TestCase):

  def test_next_successful_none_on_no_next_page_token(self):
    self.http = HttpMock(datafile('tasks.json'), {'status': '200'})
    tasks = build('tasks', 'v1', http=self.http)
    request = tasks.tasklists().list()
    self.assertEqual(None, tasks.tasklists().list_next(request, {}))

  def test_next_successful_with_next_page_token(self):
    self.http = HttpMock(datafile('tasks.json'), {'status': '200'})
    tasks = build('tasks', 'v1', http=self.http)
    request = tasks.tasklists().list()
    next_request = tasks.tasklists().list_next(
        request, {'nextPageToken': '123abc'})
    parsed = list(urlparse.urlparse(next_request.uri))
    q = parse_qs(parsed[4])
    self.assertEqual(q['pageToken'][0], '123abc')

  def test_next_with_method_with_no_properties(self):
    self.http = HttpMock(datafile('latitude.json'), {'status': '200'})
    service = build('latitude', 'v1', http=self.http)
    request = service.currentLocation().get()


class MediaGet(unittest.TestCase):

  def test_get_media(self):
    http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=http)
    request = zoo.animals().get_media(name='Lion')

    parsed = urlparse.urlparse(request.uri)
    q = parse_qs(parsed[4])
    self.assertEqual(q['alt'], ['media'])
    self.assertEqual(request.headers['accept'], '*/*')

    http = HttpMockSequence([
      ({'status': '200'}, 'standing in for media'),
      ])
    response = request.execute(http=http)
    self.assertEqual('standing in for media', response)


if __name__ == '__main__':
  unittest.main()
