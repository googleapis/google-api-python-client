# Copyright 2015 Google Inc. All rights reserved.
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

"""Unit tests for googleapiclient._helpers."""

import unittest

import mock

import six
from six.moves import urllib

from googleapiclient import _helpers


class PositionalTests(unittest.TestCase):
    def test_usage(self):
        _helpers.positional_parameters_enforcement = _helpers.POSITIONAL_EXCEPTION

        # 1 positional arg, 1 keyword-only arg.
        @_helpers.positional(1)
        def function(pos, kwonly=None):
            return True

        self.assertTrue(function(1))
        self.assertTrue(function(1, kwonly=2))
        with self.assertRaises(TypeError):
            function(1, 2)

        # No positional, but a required keyword arg.
        @_helpers.positional(0)
        def function2(required_kw):
            return True

        self.assertTrue(function2(required_kw=1))
        with self.assertRaises(TypeError):
            function2(1)

        # Unspecified positional, should automatically figure out 1 positional
        # 1 keyword-only (same as first case above).
        @_helpers.positional
        def function3(pos, kwonly=None):
            return True

        self.assertTrue(function3(1))
        self.assertTrue(function3(1, kwonly=2))
        with self.assertRaises(TypeError):
            function3(1, 2)

    @mock.patch("googleapiclient._helpers.logger")
    def test_enforcement_warning(self, mock_logger):
        _helpers.positional_parameters_enforcement = _helpers.POSITIONAL_WARNING

        @_helpers.positional(1)
        def function(pos, kwonly=None):
            return True

        self.assertTrue(function(1, 2))
        self.assertTrue(mock_logger.warning.called)

    @mock.patch("googleapiclient._helpers.logger")
    def test_enforcement_ignore(self, mock_logger):
        _helpers.positional_parameters_enforcement = _helpers.POSITIONAL_IGNORE

        @_helpers.positional(1)
        def function(pos, kwonly=None):
            return True

        self.assertTrue(function(1, 2))
        self.assertFalse(mock_logger.warning.called)


class AddQueryParameterTests(unittest.TestCase):
    def test__add_query_parameter(self):
        self.assertEqual(_helpers._add_query_parameter("/action", "a", None), "/action")
        self.assertEqual(
            _helpers._add_query_parameter("/action", "a", "b"), "/action?a=b"
        )
        self.assertEqual(
            _helpers._add_query_parameter("/action?a=b", "a", "c"), "/action?a=c"
        )
        # Order is non-deterministic.
        self.assertIn(
            _helpers._add_query_parameter("/action?a=b", "c", "d"),
            ["/action?a=b&c=d", "/action?c=d&a=b"],
        )
        self.assertEqual(
            _helpers._add_query_parameter("/action", "a", " ="), "/action?a=+%3D"
        )


def assertUrisEqual(testcase, expected, actual):
    """Test that URIs are the same, up to reordering of query parameters."""
    expected = urllib.parse.urlparse(expected)
    actual = urllib.parse.urlparse(actual)
    testcase.assertEqual(expected.scheme, actual.scheme)
    testcase.assertEqual(expected.netloc, actual.netloc)
    testcase.assertEqual(expected.path, actual.path)
    testcase.assertEqual(expected.params, actual.params)
    testcase.assertEqual(expected.fragment, actual.fragment)
    expected_query = urllib.parse.parse_qs(expected.query)
    actual_query = urllib.parse.parse_qs(actual.query)
    for name in expected_query.keys():
        testcase.assertEqual(expected_query[name], actual_query[name])
    for name in actual_query.keys():
        testcase.assertEqual(expected_query[name], actual_query[name])


class Test_update_query_params(unittest.TestCase):
    def test_update_query_params_no_params(self):
        uri = "http://www.google.com"
        updated = _helpers.update_query_params(uri, {"a": "b"})
        self.assertEqual(updated, uri + "?a=b")

    def test_update_query_params_existing_params(self):
        uri = "http://www.google.com?x=y"
        updated = _helpers.update_query_params(uri, {"a": "b", "c": "d&"})
        hardcoded_update = uri + "&a=b&c=d%26"
        assertUrisEqual(self, updated, hardcoded_update)

    def test_update_query_params_replace_param(self):
        base_uri = "http://www.google.com"
        uri = base_uri + "?x=a"
        updated = _helpers.update_query_params(uri, {"x": "b", "y": "c"})
        hardcoded_update = base_uri + "?x=b&y=c"
        assertUrisEqual(self, updated, hardcoded_update)

    def test_update_query_params_repeated_params(self):
        uri = "http://www.google.com?x=a&x=b"
        with self.assertRaises(ValueError):
            _helpers.update_query_params(uri, {"a": "c"})


class Test_parse_unique_urlencoded(unittest.TestCase):
    def test_without_repeats(self):
        content = "a=b&c=d"
        result = _helpers.parse_unique_urlencoded(content)
        self.assertEqual(result, {"a": "b", "c": "d"})

    def test_with_repeats(self):
        content = "a=b&a=d"
        with self.assertRaises(ValueError):
            _helpers.parse_unique_urlencoded(content)
