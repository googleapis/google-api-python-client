# Copyright 2020 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Directory based cache for the discovery document.

The cache is stored in a directory so that multiple processes can
share the same cache. Only reading operation is supported.

"""

from __future__ import absolute_import

__author__ = "partheniou@google.com (Anthonios Partheniou)"

import os

from . import base

def _get_discovery_doc_name(url):
    doc_name = None
    # Extract the API name and version from the url
    # https://www.googleapis.com/discovery/v1/apis/<name>/<version>/rest
    url_parts = url.split('/')
    if len(url_parts) > 3:
        doc_name = "{}.{}.json".format(url_parts[-3], url_parts[-2])
    return doc_name

class Cache(base.Cache):
    """A directory based cache for the discovery documents."""

    def __init__(self):
        """Constructor"""
        self._directory = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'documents')

    def get(self, url):
        try:
            with open(os.path.join(self._directory, _get_discovery_doc_name(url)), 'r') as f:
                content = f.read()
        except FileNotFoundError:
            content = None
        return content

    def set(self, url, content):
        # Write operations are not supported.
        pass

cache = Cache()
