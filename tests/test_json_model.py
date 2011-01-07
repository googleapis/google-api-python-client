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

from apiclient.model import JsonModel
from apiclient.errors import HttpError
import os
import unittest
import httplib2

# Python 2.5 requires different modules
try:
  from urlparse import parse_qs
except ImportError:
  from cgi import parse_qs


class Model(unittest.TestCase):
  def test_json_no_body(self):
    model = JsonModel()

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
    model = JsonModel()

    headers = {}
    path_params = {}
    query_params = {}
    body = {}

    headers, params, query, body = model.request(headers, path_params, query_params, body)

    self.assertEqual(headers['accept'], 'application/json')
    self.assertEqual(headers['content-type'], 'application/json')
    self.assertNotEqual(query, '')
    self.assertEqual(body, '{}')

  def test_json_body_default_data(self):
    """Test that a 'data' wrapper doesn't get added if one is already present."""
    model = JsonModel()

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
    model = JsonModel()

    headers = {}
    path_params = {}
    query_params = {'foo': 1, 'bar': u'\N{COMET}'}
    body = {}

    headers, params, query, body = model.request(headers, path_params, query_params, body)

    self.assertEqual(headers['accept'], 'application/json')
    self.assertEqual(headers['content-type'], 'application/json')

    query_dict = parse_qs(query)
    self.assertEqual(query_dict['foo'], ['1'])
    self.assertEqual(query_dict['bar'], [u'\N{COMET}'.encode('utf-8')])
    self.assertEqual(body, '{}')

  def test_user_agent(self):
    model = JsonModel()

    headers = {'user-agent': 'my-test-app/1.23.4'}
    path_params = {}
    query_params = {}
    body = {}

    headers, params, query, body = model.request(headers, path_params, query_params, body)

    self.assertEqual(headers['user-agent'], 'my-test-app/1.23.4 google-api-python-client/1.0')

  def test_bad_response(self):
    model = JsonModel()
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
    model = JsonModel()
    resp = httplib2.Response({'status': '200'})
    resp.reason = 'OK'
    content = '{"data": "is good"}'

    content = model.response(resp, content)
    self.assertEqual(content, 'is good')

  def test_good_response_wo_data(self):
    model = JsonModel()
    resp = httplib2.Response({'status': '200'})
    resp.reason = 'OK'
    content = '{"foo": "is good"}'

    content = model.response(resp, content)
    self.assertEqual(content, {'foo': 'is good'})

  def test_good_response_wo_data_str(self):
    model = JsonModel()
    resp = httplib2.Response({'status': '200'})
    resp.reason = 'OK'
    content = '"data goes here"'

    content = model.response(resp, content)
    self.assertEqual(content, 'data goes here')

if __name__ == '__main__':
  unittest.main()
