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

__author__ = "jcgregorio@google.com (Joe Gregorio)"

import io
import json
import platform
import unittest
import urllib

import httplib2

from googleapiclient import version as googleapiclient_version
from googleapiclient.errors import HttpError
import googleapiclient.model
from googleapiclient.model import JsonModel

try:
    from google.api_core.version_header import API_VERSION_METADATA_KEY

    HAS_API_VERSION = True
except ImportError:
    HAS_API_VERSION = False

_LIBRARY_VERSION = googleapiclient_version.__version__
CSV_TEXT_MOCK = "column1,column2,column3\nstring1,1.2,string2"


class Model(unittest.TestCase):
    def test_json_no_body(self):
        model = JsonModel(data_wrapper=False)

        headers = {}
        path_params = {}
        query_params = {}
        body = None

        headers, unused_params, query, body = model.request(
            headers, path_params, query_params, body
        )

        self.assertEqual(headers["accept"], "application/json")
        self.assertTrue("content-type" not in headers)
        self.assertNotEqual(query, "")
        self.assertEqual(body, None)

    def test_json_body(self):
        model = JsonModel(data_wrapper=False)

        headers = {}
        path_params = {}
        query_params = {}
        body = {}

        headers, unused_params, query, body = model.request(
            headers, path_params, query_params, body
        )

        self.assertEqual(headers["accept"], "application/json")
        self.assertEqual(headers["content-type"], "application/json")
        self.assertNotEqual(query, "")
        self.assertEqual(body, "{}")

    def test_json_body_data_wrapper(self):
        model = JsonModel(data_wrapper=True)

        headers = {}
        path_params = {}
        query_params = {}
        body = {}

        headers, unused_params, query, body = model.request(
            headers, path_params, query_params, body
        )

        self.assertEqual(headers["accept"], "application/json")
        self.assertEqual(headers["content-type"], "application/json")
        self.assertNotEqual(query, "")
        self.assertEqual(body, '{"data": {}}')

    def test_json_body_default_data(self):
        """Test that a 'data' wrapper doesn't get added if one is already present."""
        model = JsonModel(data_wrapper=True)

        headers = {}
        path_params = {}
        query_params = {}
        body = {"data": "foo"}

        headers, unused_params, query, body = model.request(
            headers, path_params, query_params, body
        )

        self.assertEqual(headers["accept"], "application/json")
        self.assertEqual(headers["content-type"], "application/json")
        self.assertNotEqual(query, "")
        self.assertEqual(body, '{"data": "foo"}')

    def test_json_build_query(self):
        model = JsonModel(data_wrapper=False)

        headers = {}
        path_params = {}
        query_params = {
            "foo": 1,
            "bar": "\N{COMET}",
            "baz": ["fe", "fi", "fo", "fum"],  # Repeated parameters
            "qux": [],
        }
        body = {}

        headers, unused_params, query, body = model.request(
            headers, path_params, query_params, body
        )

        self.assertEqual(headers["accept"], "application/json")
        self.assertEqual(headers["content-type"], "application/json")

        query_dict = urllib.parse.parse_qs(query[1:])
        self.assertEqual(query_dict["foo"], ["1"])
        self.assertEqual(query_dict["bar"], ["\N{COMET}"])
        self.assertEqual(query_dict["baz"], ["fe", "fi", "fo", "fum"])
        self.assertTrue("qux" not in query_dict)
        self.assertEqual(body, "{}")

    def test_user_agent(self):
        model = JsonModel(data_wrapper=False)

        headers = {"user-agent": "my-test-app/1.23.4"}
        path_params = {}
        query_params = {}
        body = {}

        headers, unused_params, unused_query, body = model.request(
            headers, path_params, query_params, body
        )

        self.assertEqual(headers["user-agent"], "my-test-app/1.23.4 (gzip)")

    def test_x_goog_api_client(self):
        model = JsonModel(data_wrapper=False)

        # test header composition for cloud clients that wrap discovery
        headers = {"x-goog-api-client": "gccl/1.23.4"}
        path_params = {}
        query_params = {}
        body = {}

        headers, unused_params, unused_query, body = model.request(
            headers, path_params, query_params, body
        )

        self.assertEqual(
            headers["x-goog-api-client"],
            "gccl/1.23.4"
            + " gdcl/"
            + _LIBRARY_VERSION
            + " gl-python/"
            + platform.python_version(),
        )

    @unittest.skipIf(
        not HAS_API_VERSION,
        "Skip this test when an older version of google-api-core is used",
    )
    def test_x_goog_api_version(self):
        model = JsonModel(data_wrapper=False)

        # test header composition for clients that wrap discovery
        headers = {}
        path_params = {}
        query_params = {}
        body = {}
        api_version = "20240401"

        headers, _, _, body = model.request(
            headers, path_params, query_params, body, api_version
        )

        self.assertEqual(
            headers[API_VERSION_METADATA_KEY],
            api_version,
        )

    def test_bad_response(self):
        model = JsonModel(data_wrapper=False)
        resp = httplib2.Response({"status": "401"})
        resp.reason = "Unauthorized"
        content = b'{"error": {"message": "not authorized"}}'

        try:
            content = model.response(resp, content)
            self.fail("Should have thrown an exception")
        except HttpError as e:
            self.assertTrue("not authorized" in str(e))

        resp["content-type"] = "application/json"

        try:
            content = model.response(resp, content)
            self.fail("Should have thrown an exception")
        except HttpError as e:
            self.assertTrue("not authorized" in str(e))

    def test_good_response(self):
        model = JsonModel(data_wrapper=True)
        resp = httplib2.Response({"status": "200"})
        resp.reason = "OK"
        content = '{"data": "is good"}'

        content = model.response(resp, content)
        self.assertEqual(content, "is good")

    def test_good_response_wo_data(self):
        model = JsonModel(data_wrapper=False)
        resp = httplib2.Response({"status": "200"})
        resp.reason = "OK"
        content = '{"foo": "is good"}'

        content = model.response(resp, content)
        self.assertEqual(content, {"foo": "is good"})

    def test_good_response_wo_data_str(self):
        model = JsonModel(data_wrapper=False)
        resp = httplib2.Response({"status": "200"})
        resp.reason = "OK"
        content = '"data goes here"'

        content = model.response(resp, content)
        self.assertEqual(content, "data goes here")

    def test_no_content_response(self):
        model = JsonModel(data_wrapper=False)
        resp = httplib2.Response({"status": "204"})
        resp.reason = "No Content"
        content = ""

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
                self.status = items["status"]
                for key, value in items.items():
                    self[key] = value

        old_logging = googleapiclient.model.LOGGER
        googleapiclient.model.LOGGER = MockLogging()
        googleapiclient.model.dump_request_response = True
        model = JsonModel()
        request_body = {"field1": "value1", "field2": "value2"}
        body_string = model.request({}, {}, {}, request_body)[-1]
        json_body = json.loads(body_string)
        self.assertEqual(request_body, json_body)

        response = {
            "status": 200,
            "response_field_1": "response_value_1",
            "response_field_2": "response_value_2",
        }
        response_body = model.response(MockResponse(response), body_string)
        self.assertEqual(request_body, response_body)
        self.assertEqual(
            googleapiclient.model.LOGGER.info_record[:2],
            ["--request-start--", "-headers-start-"],
        )
        self.assertTrue(
            "response_field_1: response_value_1"
            in googleapiclient.model.LOGGER.info_record
        )
        self.assertTrue(
            "response_field_2: response_value_2"
            in googleapiclient.model.LOGGER.info_record
        )
        self.assertEqual(
            json.loads(googleapiclient.model.LOGGER.info_record[-2]), request_body
        )
        self.assertEqual(
            googleapiclient.model.LOGGER.info_record[-1], "--response-end--"
        )
        googleapiclient.model.LOGGER = old_logging

    def test_no_data_wrapper_deserialize(self):
        model = JsonModel(data_wrapper=False)
        resp = httplib2.Response({"status": "200"})
        resp.reason = "OK"
        content = '{"data": "is good"}'
        content = model.response(resp, content)
        self.assertEqual(content, {"data": "is good"})

    def test_no_data_wrapper_deserialize_text_format(self):
        model = JsonModel(data_wrapper=False)
        resp = httplib2.Response({"status": "200"})
        resp.reason = "OK"
        content = CSV_TEXT_MOCK
        content = model.response(resp, content)
        self.assertEqual(content, CSV_TEXT_MOCK)

    def test_no_data_wrapper_deserialize_raise_type_error(self):
        buffer = io.StringIO()
        buffer.write("String buffer")
        model = JsonModel(data_wrapper=False)
        resp = httplib2.Response({"status": "500"})
        resp.reason = "The JSON object must be str, bytes or bytearray, not StringIO"
        content = buffer
        with self.assertRaises(TypeError):
            model.response(resp, content)

    def test_data_wrapper_deserialize(self):
        model = JsonModel(data_wrapper=True)
        resp = httplib2.Response({"status": "200"})
        resp.reason = "OK"
        content = '{"data": "is good"}'
        content = model.response(resp, content)
        self.assertEqual(content, "is good")

    def test_data_wrapper_deserialize_nodata(self):
        model = JsonModel(data_wrapper=True)
        resp = httplib2.Response({"status": "200"})
        resp.reason = "OK"
        content = '{"atad": "is good"}'
        content = model.response(resp, content)
        self.assertEqual(content, {"atad": "is good"})


if __name__ == "__main__":
    unittest.main()
