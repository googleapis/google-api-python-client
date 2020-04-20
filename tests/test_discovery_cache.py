#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

"""Discovery document cache tests."""

import datetime
import unittest2 as unittest

import mock

from googleapiclient.discovery_cache import DISCOVERY_DOC_MAX_AGE
from googleapiclient.discovery_cache.base import Cache

try:
    from googleapiclient.discovery_cache.file_cache import Cache as FileCache
except ImportError:
    FileCache = None


@unittest.skipIf(FileCache is None, "FileCache unavailable.")
class FileCacheTest(unittest.TestCase):
    @mock.patch(
        "googleapiclient.discovery_cache.file_cache.FILENAME",
        new="google-api-python-client-discovery-doc-tests.cache",
    )
    def test_expiration(self):
        def future_now():
            return datetime.datetime.now() + datetime.timedelta(
                seconds=DISCOVERY_DOC_MAX_AGE
            )

        mocked_datetime = mock.MagicMock()
        mocked_datetime.datetime.now.side_effect = future_now
        cache = FileCache(max_age=DISCOVERY_DOC_MAX_AGE)
        first_url = "url-1"
        first_url_content = "url-1-content"
        cache.set(first_url, first_url_content)

        # Make sure the content is cached.
        self.assertEqual(first_url_content, cache.get(first_url))

        # Simulate another `set` call in the future date.
        with mock.patch(
            "googleapiclient.discovery_cache.file_cache.datetime", new=mocked_datetime
        ):
            cache.set("url-2", "url-2-content")

        # Make sure the content is expired
        self.assertEqual(None, cache.get(first_url))
