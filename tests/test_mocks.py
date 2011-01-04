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

"""Mock tests

Unit tests for the Mocks.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

from apiclient.discovery import HttpError
from apiclient.discovery import build
from apiclient.http import RequestMockBuilder
from tests.util import HttpMock

import unittest
import httplib2


class Mocks(unittest.TestCase):
  def setUp(self):
    self.http = HttpMock('buzz.json', {'status': '200'})

  def test_default_response(self):
    requestBuilder = RequestMockBuilder({})
    buzz = build('buzz', 'v1', http=self.http, requestBuilder=requestBuilder)
    activity = buzz.activities().get(postId='tag:blah', userId='@me').execute()
    self.assertEqual({}, activity)

  def test_simple_response(self):
    requestBuilder = RequestMockBuilder({
        'chili.activities.get': (None, '{"data": {"foo": "bar"}}')
        })
    buzz = build('buzz', 'v1', http=self.http, requestBuilder=requestBuilder)

    activity = buzz.activities().get(postId='tag:blah', userId='@me').execute()
    self.assertEqual({"foo": "bar"}, activity)


  def test_errors(self):
    errorResponse = httplib2.Response({'status': 500, 'reason': 'Server Error'})
    requestBuilder = RequestMockBuilder({
        'chili.activities.list': (errorResponse, '{}')
        })
    buzz = build('buzz', 'v1', http=self.http, requestBuilder=requestBuilder)

    try:
      activity = buzz.activities().list(scope='@self', userId='@me').execute()
      self.fail('An exception should have been thrown')
    except HttpError, e:
      self.assertEqual('{}', e.content)
      self.assertEqual(500, e.resp.status)
      self.assertEqual('Server Error', e.resp.reason)




if __name__ == '__main__':
  unittest.main()
