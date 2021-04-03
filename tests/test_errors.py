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

"""Tests for errors handling
"""
from __future__ import absolute_import

__author__ = "afshar@google.com (Ali Afshar)"


import unittest2 as unittest
import httplib2


from googleapiclient.errors import HttpError


JSON_ERROR_CONTENT = b"""
{
 "error": {
  "errors": [
   {
    "domain": "global",
    "reason": "required",
    "message": "country is required",
    "locationType": "parameter",
    "location": "country"
   }
  ],
  "code": 400,
  "message": "country is required",
  "details": "error details"
 }
}
"""

JSON_ERROR_CONTENT_NO_DETAIL = b"""
{
 "error": {
  "errors": [
   {
    "domain": "global",
    "reason": "required",
    "message": "country is required",
    "locationType": "parameter",
    "location": "country"
   }
  ],
  "code": 400,
  "message": "country is required"
 }
}
"""


def fake_response(data, headers, reason="Ok"):
    response = httplib2.Response(headers)
    response.reason = reason
    return response, data


class Error(unittest.TestCase):
    """Test handling of error bodies."""

    def test_json_body(self):
        """Test a nicely formed, expected error response."""
        resp, content = fake_response(
            JSON_ERROR_CONTENT,
            {"status": "400", "content-type": "application/json"},
            reason="Failed",
        )
        error = HttpError(resp, content, uri="http://example.org")
        self.assertEqual(error.error_details, "error details")
        self.assertEqual(error.status_code, 400)
        self.assertEqual(
            str(error),
            '<HttpError 400 when requesting http://example.org returned "country is required". Details: "error details">',
        )

    def test_bad_json_body(self):
        """Test handling of bodies with invalid json."""
        resp, content = fake_response(
            b"{", {"status": "400", "content-type": "application/json"}, reason="Failed"
        )
        error = HttpError(resp, content)
        self.assertEqual(str(error), '<HttpError 400 when requesting None returned "Failed". Details: "{">')

    def test_with_uri(self):
        """Test handling of passing in the request uri."""
        resp, content = fake_response(
            b"{",
            {"status": "400", "content-type": "application/json"},
            reason="Failure",
        )
        error = HttpError(resp, content, uri="http://example.org")
        self.assertEqual(
            str(error),
            '<HttpError 400 when requesting http://example.org returned "Failure". Details: "{">',
        )

    def test_missing_message_json_body(self):
        """Test handling of bodies with missing expected 'message' element."""
        resp, content = fake_response(
            b"{}",
            {"status": "400", "content-type": "application/json"},
            reason="Failed",
        )
        error = HttpError(resp, content)
        self.assertEqual(str(error), '<HttpError 400 "Failed">')

    def test_non_json(self):
        """Test handling of non-JSON bodies"""
        resp, content = fake_response(b"Invalid request", {"status": "400"})
        error = HttpError(resp, content)
        self.assertEqual(str(error), '<HttpError 400 when requesting None returned "Ok". Details: "Invalid request">')

    def test_missing_reason(self):
        """Test an empty dict with a missing resp.reason."""
        resp, content = fake_response(b"}NOT OK", {"status": "400"}, reason=None)
        error = HttpError(resp, content)
        self.assertEqual(str(error), '<HttpError 400 when requesting None returned "". Details: "}NOT OK">')

    def test_error_detail_for_missing_message_in_error(self):
        """Test handling of data with missing 'details' or 'detail' element."""
        resp, content = fake_response(
            JSON_ERROR_CONTENT_NO_DETAIL,
            {"status": "400", "content-type": "application/json"},
            reason="Failed",
        )
        error = HttpError(resp, content)
        expected_error_details = "[{'domain': 'global', 'reason': 'required', 'message': 'country is required', 'locationType': 'parameter', 'location': 'country'}]"
        self.assertEqual(str(error), '<HttpError 400 when requesting None returned "country is required". Details: "%s">' % expected_error_details)
        self.assertEqual(str(error.error_details), expected_error_details)
