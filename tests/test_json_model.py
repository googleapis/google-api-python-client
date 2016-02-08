#!/usr/bin/env python
#
# Copyright 2014 Google Inc. All Rights Reserved.
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
from __future__ import absolute_import
import six

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import copy
import json
import os
import unittest2 as unittest
import httplib2
import googleapiclient.model

from googleapiclient import __version__
from googleapiclient.errors import HttpError
from googleapiclient.model import JsonModel

from six.moves.urllib.parse import parse_qs


class Model(unittest.TestCase):
  def test_json_no_body(self):
    model = JsonModel(data_wrapper=False)

    headers = {}
    path_params = {}
    query_params = {}
    body = None

    headers, unused_params, query, body = model.request(
        headers, path_params, query_params, body)

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

    headers, unused_params, query, body = model.request(
        headers, path_params, query_params, body)

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

    headers, unused_params, query, body = model.request(
        headers, path_params, query_params, body)

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

    headers, unused_params, query, body = model.request(
        headers, path_params, query_params, body)

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

    headers, unused_params, query, body = model.request(
        headers, path_params, query_params, body)

    self.assertEqual(headers['accept'], 'application/json')
    self.assertEqual(headers['content-type'], 'application/json')

    query_dict = parse_qs(query[1:])
    self.assertEqual(query_dict['foo'], ['1'])
    if six.PY3:
      # Python 3, no need to encode
      self.assertEqual(query_dict['bar'], [u'\N{COMET}'])
    else:
      # Python 2, encode string
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

    headers, unused_params, unused_query, body = model.request(
        headers, path_params, query_params, body)

    self.assertEqual(headers['user-agent'],
        'my-test-app/1.23.4 google-api-python-client/' + __version__ +
        ' (gzip)')

  def test_bad_response(self):
    model = JsonModel(data_wrapper=False)
    resp = httplib2.Response({'status': '401'})
    resp.reason = 'Unauthorized'
    content = b'{"error": {"message": "not authorized"}}'

    try:
      content = model.response(resp, content)
      self.fail('Should have thrown an exception')
    except HttpError as e:
      self.assertTrue('not authorized' in str(e))

    resp['content-type'] = 'application/json'

    try:
      content = model.response(resp, content)
      self.fail('Should have thrown an exception')
    except HttpError as e:
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
        for key, value in six.iteritems(items):
          self[key] = value
    old_logging = googleapiclient.model.LOGGER
    googleapiclient.model.LOGGER = MockLogging()
    googleapiclient.model.dump_request_response = True
    model = JsonModel()
    request_body = {
        'field1': 'value1',
        'field2': 'value2'
        }
    body_string = model.request({}, {}, {}, request_body)[-1]
    json_body = json.loads(body_string)
    self.assertEqual(request_body, json_body)

    response = {'status': 200,
                'response_field_1': 'response_value_1',
                'response_field_2': 'response_value_2'}
    response_body = model.response(MockResponse(response), body_string)
    self.assertEqual(request_body, response_body)
    self.assertEqual(googleapiclient.model.LOGGER.info_record[:2],
                     ['--request-start--',
                      '-headers-start-'])
    self.assertTrue('response_field_1: response_value_1' in
                    googleapiclient.model.LOGGER.info_record)
    self.assertTrue('response_field_2: response_value_2' in
                    googleapiclient.model.LOGGER.info_record)
    self.assertEqual(json.loads(googleapiclient.model.LOGGER.info_record[-2]),
                     request_body)
    self.assertEqual(googleapiclient.model.LOGGER.info_record[-1],
                     '--response-end--')
    googleapiclient.model.LOGGER = old_logging

  def test_no_data_wrapper_deserialize(self):
    model = JsonModel(data_wrapper=False)
    resp = httplib2.Response({'status': '200'})
    resp.reason = 'OK'
    content = '{"data": "is good"}'
    content = model.response(resp, content)
    self.assertEqual(content, {'data': 'is good'})

  def test_data_wrapper_deserialize(self):
    model = JsonModel(data_wrapper=True)
    resp = httplib2.Response({'status': '200'})
    resp.reason = 'OK'
    content = '{"data": "is good"}'
    content = model.response(resp, content)
    self.assertEqual(content, 'is good')

  def test_data_wrapper_deserialize_nodata(self):
    model = JsonModel(data_wrapper=True)
    resp = httplib2.Response({'status': '200'})
    resp.reason = 'OK'
    content = '{"atad": "is good"}'
    content = model.response(resp, content)
    self.assertEqual(content, {'atad': 'is good'})



if __name__ == '__main__':
  unittest.main()
