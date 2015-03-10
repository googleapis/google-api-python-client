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

"""Protocol Buffer Model tests

Unit tests for the Protocol Buffer model.
"""
from __future__ import absolute_import

__author__ = 'mmcdonald@google.com (Matt McDonald)'

import unittest2 as unittest
import httplib2
import googleapiclient.model

from googleapiclient.errors import HttpError
from googleapiclient.model import ProtocolBufferModel

from six.moves.urllib.parse import parse_qs


class MockProtocolBuffer(object):
  def __init__(self, data=None):
    self.data = data

  def __eq__(self, other):
    return self.data == other.data

  @classmethod
  def FromString(cls, string):
    return cls(string)

  def SerializeToString(self):
    return self.data


class Model(unittest.TestCase):
  def setUp(self):
    self.model = ProtocolBufferModel(MockProtocolBuffer)

  def test_no_body(self):
    headers = {}
    path_params = {}
    query_params = {}
    body = None

    headers, params, query, body = self.model.request(
        headers, path_params, query_params, body)

    self.assertEqual(headers['accept'], 'application/x-protobuf')
    self.assertTrue('content-type' not in headers)
    self.assertNotEqual(query, '')
    self.assertEqual(body, None)

  def test_body(self):
    headers = {}
    path_params = {}
    query_params = {}
    body = MockProtocolBuffer('data')

    headers, params, query, body = self.model.request(
        headers, path_params, query_params, body)

    self.assertEqual(headers['accept'], 'application/x-protobuf')
    self.assertEqual(headers['content-type'], 'application/x-protobuf')
    self.assertNotEqual(query, '')
    self.assertEqual(body, 'data')

  def test_good_response(self):
    resp = httplib2.Response({'status': '200'})
    resp.reason = 'OK'
    content = 'data'

    content = self.model.response(resp, content)
    self.assertEqual(content, MockProtocolBuffer('data'))

  def test_no_content_response(self):
    resp = httplib2.Response({'status': '204'})
    resp.reason = 'No Content'
    content = ''

    content = self.model.response(resp, content)
    self.assertEqual(content, MockProtocolBuffer())


if __name__ == '__main__':
  unittest.main()
