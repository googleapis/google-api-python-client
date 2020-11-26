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

"""Caching utility for the discovery document."""

from __future__ import absolute_import

import logging
import datetime
import os

LOGGER = logging.getLogger(__name__)

DISCOVERY_DOC_MAX_AGE = 60 * 60 * 24  # 1 day
DISCOVERY_DOC_DIR = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'documents')

def autodetect():
    """Detects an appropriate cache module and returns it.

  Returns:
    googleapiclient.discovery_cache.base.Cache, a cache object which
    is auto detected, or None if no cache object is available.
  """
    if 'APPENGINE_RUNTIME' in os.environ:
        try:
            from google.appengine.api import memcache
            from . import appengine_memcache

            return appengine_memcache.cache
        except Exception:
            pass
    try:
        from . import file_cache

        return file_cache.cache
    except Exception:
        LOGGER.info("file_cache is only supported with oauth2client<4.0.0",
            exc_info=False)
        return None

def get_static_doc(uri):
    """Retrieves the discovery document from the directory defined in
    DISCOVERY_DOC_STATIC_DIR corresponding to the uri provided.

    Args:
        uri: string, The URI of the discovery document in the format
        https://{domain}/discovery/{discoveryVer}/apis/{api}/{apiVersion}/rest

    Returns:
        A string containing the contents of the JSON discovery document,
        otherwise None if the JSON discovery document was not found.
    """

    doc_name = None
    content = None

    # Extract the {apiVersion} and {api} from the uri which are the 2nd and 3rd
    # last parts of the uri respectively.
    # https://www.googleapis.com/discovery/v1/apis/{api}/{apiVersion}/rest
    uri_parts = uri.split('/')
    if len(uri_parts) > 3:
        doc_name = "{}.{}.json".format(uri_parts[-3], uri_parts[-2])

        try:
            with open(os.path.join(DISCOVERY_DOC_DIR, doc_name), 'r') as f:
                content = f.read()
        except FileNotFoundError:
            # File does not exist. Nothing to do here.
            pass

    return content

