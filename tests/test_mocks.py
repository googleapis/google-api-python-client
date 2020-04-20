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

"""Mock tests

Unit tests for the Mocks.
"""
from __future__ import absolute_import

__author__ = "jcgregorio@google.com (Joe Gregorio)"

import httplib2
import os
import unittest2 as unittest

from googleapiclient.errors import HttpError
from googleapiclient.errors import UnexpectedBodyError
from googleapiclient.errors import UnexpectedMethodError
from googleapiclient.discovery import build
from googleapiclient.http import RequestMockBuilder
from googleapiclient.http import HttpMock


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def datafile(filename):
    return os.path.join(DATA_DIR, filename)


class Mocks(unittest.TestCase):
    def setUp(self):
        self.http = HttpMock(datafile("plus.json"), {"status": "200"})
        self.zoo_http = HttpMock(datafile("zoo.json"), {"status": "200"})

    def test_default_response(self):
        requestBuilder = RequestMockBuilder({})
        plus = build("plus", "v1", http=self.http, requestBuilder=requestBuilder)
        activity = plus.activities().get(activityId="tag:blah").execute()
        self.assertEqual({}, activity)

    def test_simple_response(self):
        requestBuilder = RequestMockBuilder(
            {"plus.activities.get": (None, '{"foo": "bar"}')}
        )
        plus = build("plus", "v1", http=self.http, requestBuilder=requestBuilder)

        activity = plus.activities().get(activityId="tag:blah").execute()
        self.assertEqual({"foo": "bar"}, activity)

    def test_unexpected_call(self):
        requestBuilder = RequestMockBuilder({}, check_unexpected=True)

        plus = build("plus", "v1", http=self.http, requestBuilder=requestBuilder)

        try:
            plus.activities().get(activityId="tag:blah").execute()
            self.fail("UnexpectedMethodError should have been raised")
        except UnexpectedMethodError:
            pass

    def test_simple_unexpected_body(self):
        requestBuilder = RequestMockBuilder(
            {"zoo.animals.insert": (None, '{"data": {"foo": "bar"}}', None)}
        )
        zoo = build("zoo", "v1", http=self.zoo_http, requestBuilder=requestBuilder)

        try:
            zoo.animals().insert(body="{}").execute()
            self.fail("UnexpectedBodyError should have been raised")
        except UnexpectedBodyError:
            pass

    def test_simple_expected_body(self):
        requestBuilder = RequestMockBuilder(
            {"zoo.animals.insert": (None, '{"data": {"foo": "bar"}}', "{}")}
        )
        zoo = build("zoo", "v1", http=self.zoo_http, requestBuilder=requestBuilder)

        try:
            zoo.animals().insert(body="").execute()
            self.fail("UnexpectedBodyError should have been raised")
        except UnexpectedBodyError:
            pass

    def test_simple_wrong_body(self):
        requestBuilder = RequestMockBuilder(
            {
                "zoo.animals.insert": (
                    None,
                    '{"data": {"foo": "bar"}}',
                    '{"data": {"foo": "bar"}}',
                )
            }
        )
        zoo = build("zoo", "v1", http=self.zoo_http, requestBuilder=requestBuilder)

        try:
            zoo.animals().insert(body='{"data": {"foo": "blah"}}').execute()
            self.fail("UnexpectedBodyError should have been raised")
        except UnexpectedBodyError:
            pass

    def test_simple_matching_str_body(self):
        requestBuilder = RequestMockBuilder(
            {
                "zoo.animals.insert": (
                    None,
                    '{"data": {"foo": "bar"}}',
                    '{"data": {"foo": "bar"}}',
                )
            }
        )
        zoo = build("zoo", "v1", http=self.zoo_http, requestBuilder=requestBuilder)

        activity = zoo.animals().insert(body={"data": {"foo": "bar"}}).execute()
        self.assertEqual({"foo": "bar"}, activity)

    def test_simple_matching_dict_body(self):
        requestBuilder = RequestMockBuilder(
            {
                "zoo.animals.insert": (
                    None,
                    '{"data": {"foo": "bar"}}',
                    {"data": {"foo": "bar"}},
                )
            }
        )
        zoo = build("zoo", "v1", http=self.zoo_http, requestBuilder=requestBuilder)

        activity = zoo.animals().insert(body={"data": {"foo": "bar"}}).execute()
        self.assertEqual({"foo": "bar"}, activity)

    def test_errors(self):
        errorResponse = httplib2.Response({"status": 500, "reason": "Server Error"})
        requestBuilder = RequestMockBuilder(
            {"plus.activities.list": (errorResponse, b"{}")}
        )
        plus = build("plus", "v1", http=self.http, requestBuilder=requestBuilder)

        try:
            activity = (
                plus.activities().list(collection="public", userId="me").execute()
            )
            self.fail("An exception should have been thrown")
        except HttpError as e:
            self.assertEqual(b"{}", e.content)
            self.assertEqual(500, e.resp.status)
            self.assertEqual("Server Error", e.resp.reason)


if __name__ == "__main__":
    unittest.main()
