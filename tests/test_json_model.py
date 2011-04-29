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

"""JSON Model tests

Unit tests for the JSON model.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import copy
import gflags
import os
import unittest
import httplib2
import apiclient.model

from apiclient.anyjson import simplejson
from apiclient.errors import HttpError
from apiclient.model import JsonModel

FLAGS = gflags.FLAGS

# Python 2.5 requires different modules
try:
  from urlparse import parse_qs
except ImportError:
  from cgi import parse_qs


class Model(unittest.TestCase):
  def test_json_no_body(self):
    model = JsonModel(data_wrapper=False)

    headers = {}
    path_params = {}
    query_params = {}
    body = None

    headers, params, query, body = model.request(headers, path_params, query_params, body)

    self.assertEqual(headers['accept'], 'application/json')
    self.assertTrue('content-type' not in headers)
    self.assertNotEqual(query, '')
    self.assertEqual(body, None)

  def test_json_body(self):
    model = JsonModel(data_wrapper=False)

    headers = {}
    path_params = {}
    query_params = {}
    body = {}

    headers, params, query, body = model.request(headers, path_params, query_params, body)

    self.assertEqual(headers['accept'], 'application/json')
    self.assertEqual(headers['content-type'], 'application/json')
    self.assertNotEqual(query, '')
    self.assertEqual(body, '{}')

  def test_json_body_data_wrapper(self):
    model = JsonModel(data_wrapper=True)

    headers = {}
    path_params = {}
    query_params = {}
    body = {}

    headers, params, query, body = model.request(headers, path_params, query_params, body)

    self.assertEqual(headers['accept'], 'application/json')
    self.assertEqual(headers['content-type'], 'application/json')
    self.assertNotEqual(query, '')
    self.assertEqual(body, '{"data": {}}')

  def test_json_body_default_data(self):
    """Test that a 'data' wrapper doesn't get added if one is already present."""
    model = JsonModel(data_wrapper=True)

    headers = {}
    path_params = {}
    query_params = {}
    body = {'data': 'foo'}

    headers, params, query, body = model.request(headers, path_params, query_params, body)

    self.assertEqual(headers['accept'], 'application/json')
    self.assertEqual(headers['content-type'], 'application/json')
    self.assertNotEqual(query, '')
    self.assertEqual(body, '{"data": "foo"}')

  def test_json_build_query(self):
    model = JsonModel(data_wrapper=False)

    headers = {}
    path_params = {}
    query_params = {'foo': 1, 'bar': u'\N{COMET}',
        'baz': ['fe', 'fi', 'fo', 'fum'], # Repeated parameters
        'qux': []}
    body = {}

    headers, params, query, body = model.request(headers, path_params, query_params, body)

    self.assertEqual(headers['accept'], 'application/json')
    self.assertEqual(headers['content-type'], 'application/json')

    query_dict = parse_qs(query[1:])
    self.assertEqual(query_dict['foo'], ['1'])
    self.assertEqual(query_dict['bar'], [u'\N{COMET}'.encode('utf-8')])
    self.assertEqual(query_dict['baz'], ['fe', 'fi', 'fo', 'fum'])
    self.assertTrue('qux' not in query_dict)
    self.assertEqual(body, '{}')

  def test_user_agent(self):
    model = JsonModel(data_wrapper=False)

    headers = {'user-agent': 'my-test-app/1.23.4'}
    path_params = {}
    query_params = {}
    body = {}

    headers, params, query, body = model.request(headers, path_params, query_params, body)

    self.assertEqual(headers['user-agent'], 'my-test-app/1.23.4 google-api-python-client/1.0')

  def test_bad_response(self):
    model = JsonModel(data_wrapper=False)
    resp = httplib2.Response({'status': '401'})
    resp.reason = 'Unauthorized'
    content = '{"error": {"message": "not authorized"}}'

    try:
      content = model.response(resp, content)
      self.fail('Should have thrown an exception')
    except HttpError, e:
      self.assertTrue('Unauthorized' in str(e))

    resp['content-type'] = 'application/json'

    try:
      content = model.response(resp, content)
      self.fail('Should have thrown an exception')
    except HttpError, e:
      self.assertTrue('not authorized' in str(e))


  def test_good_response(self):
    model = JsonModel(data_wrapper=True)
    resp = httplib2.Response({'status': '200'})
    resp.reason = 'OK'
    content = '{"data": "is good"}'

    content = model.response(resp, content)
    self.assertEqual(content, 'is good')

  def test_good_response_wo_data(self):
    model = JsonModel(data_wrapper=False)
    resp = httplib2.Response({'status': '200'})
    resp.reason = 'OK'
    content = '{"foo": "is good"}'

    content = model.response(resp, content)
    self.assertEqual(content, {'foo': 'is good'})

  def test_good_response_wo_data_str(self):
    model = JsonModel(data_wrapper=False)
    resp = httplib2.Response({'status': '200'})
    resp.reason = 'OK'
    content = '"data goes here"'

    content = model.response(resp, content)
    self.assertEqual(content, 'data goes here')

  def test_no_content_response(self):
    model = JsonModel(data_wrapper=False)
    resp = httplib2.Response({'status': '204'})
    resp.reason = 'No Content'
    content = ''

    content = model.response(resp, content)
    self.assertEqual(content, {})

  def test_logging(self):
    class MockLogging(object):
      def __init__(self):
        self.info_record = []
        self.debug_record = []
      def info(self, message, *args):
        self.info_record.append(message % args)

      def debug(self, message, *args):
        self.debug_record.append(message % args)

    class MockResponse(dict):
      def __init__(self, items):
        super(MockResponse, self).__init__()
        self.status = items['status']
        for key, value in items.iteritems():
          self[key] = value
    old_logging = apiclient.model.logging
    apiclient.model.logging = MockLogging()
    apiclient.model.FLAGS = copy.deepcopy(FLAGS)
    apiclient.model.FLAGS.dump_request_response = True
    model = JsonModel()
    request_body = {
        'field1': 'value1',
        'field2': 'value2'
        }
    body_string = model.request({}, {}, {}, request_body)[-1]
    json_body = simplejson.loads(body_string)
    self.assertEqual(request_body, json_body)

    response = {'status': 200,
                'response_field_1': 'response_value_1',
                'response_field_2': 'response_value_2'}
    response_body = model.response(MockResponse(response), body_string)
    self.assertEqual(request_body, response_body)
    self.assertEqual(apiclient.model.logging.info_record[:2],
                     ['--request-start--',
                      '-headers-start-'])
    self.assertTrue('response_field_1: response_value_1' in
                    apiclient.model.logging.info_record)
    self.assertTrue('response_field_2: response_value_2' in
                    apiclient.model.logging.info_record)
    self.assertEqual(simplejson.loads(apiclient.model.logging.info_record[-2]),
                     request_body)
    self.assertEqual(apiclient.model.logging.info_record[-1],
                     '--response-end--')
    apiclient.model.logging = old_logging


if __name__ == '__main__':
  unittest.main()
