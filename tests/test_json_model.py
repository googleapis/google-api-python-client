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

from apiclient.discovery import JsonModel
import os
import unittest
import urlparse


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
    self.assertEqual(body, '{"data": {}}')

  def test_json_build_query(self):
    model = JsonModel()

    headers = {}
    path_params = {}
    query_params = {'foo': 1, 'bar': u'\N{COMET}'}
    body = {}

    headers, params, query, body = model.request(headers, path_params, query_params, body)

    self.assertEqual(headers['accept'], 'application/json')
    self.assertEqual(headers['content-type'], 'application/json')

    query_dict = urlparse.parse_qs(query)
    self.assertEqual(query_dict['foo'], ['1'])
    self.assertEqual(query_dict['bar'], [u'\N{COMET}'.encode('utf-8')])
    self.assertEqual(body, '{"data": {}}')


if __name__ == '__main__':
  unittest.main()
