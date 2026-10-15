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

import getpass
import logging
import os
import stat
import tempfile

LOGGER = logging.getLogger(__name__)

DISCOVERY_DOC_MAX_AGE = 60 * 60 * 24  # 1 day
DISCOVERY_DOC_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "documents"
)

_CACHE_SUBDIR_PREFIX = "google-api-python-client-discovery-cache-"


def _get_cache_directory():
    """Return a private, per-user directory for file based discovery caches.

    The file based discovery cache was historically written to a fixed,
    world-predictable file name directly in the shared system temporary
    directory (for example ``/tmp`` on Linux, which is writable by every
    local user). Any local user could pre-create, replace, read, or symlink
    that file and poison the cached discovery document. Because a discovery
    document controls ``rootUrl``, a poisoned entry redirects every later
    authenticated request, including the caller's OAuth credentials, to an
    attacker chosen host.

    Keep the cache inside a per-user directory created with ``0o700`` so
    other local users cannot access it, and refuse to use the directory when
    it is not a regular directory owned by the current user with no access
    for group or others.
    """
    if hasattr(os, "getuid"):
        suffix = str(os.getuid())
    else:
        try:
            raw = getpass.getuser()
        except Exception:
            raw = ""
        suffix = "".join(c for c in raw if c.isalnum() or c in "._-") or "default"

    cache_dir = os.path.join(tempfile.gettempdir(), _CACHE_SUBDIR_PREFIX + suffix)
    os.makedirs(cache_dir, exist_ok=True)

    if hasattr(os, "getuid"):
        try:
            os.chmod(cache_dir, 0o700)
        except OSError:
            pass
        info = os.lstat(cache_dir)
        if (
            not stat.S_ISDIR(info.st_mode)
            or info.st_uid != os.getuid()
            or info.st_mode & 0o077
        ):
            raise OSError(
                "Refusing to use discovery cache directory %r: it must be a "
                "directory owned by the current user with no group or other "
                "access" % cache_dir
            )

    return cache_dir


def autodetect():
    """Detects an appropriate cache module and returns it.

    Returns:
      googleapiclient.discovery_cache.base.Cache, a cache object which
      is auto detected, or None if no cache object is available.
    """
    if "GAE_ENV" in os.environ:
        try:
            from . import appengine_memcache

            return appengine_memcache.cache
        except Exception:
            pass
    try:
        from . import file_cache

        return file_cache.cache
    except Exception:
        LOGGER.info(
            "file_cache is only supported with oauth2client<4.0.0", exc_info=False
        )
        return None


def get_static_doc(serviceName, version):
    """Retrieves the discovery document from the directory defined in
    DISCOVERY_DOC_DIR corresponding to the serviceName and version provided.

    Args:
        serviceName: string, name of the service.
        version: string, the version of the service.

    Returns:
        A string containing the contents of the JSON discovery document,
        otherwise None if the JSON discovery document was not found.
    """

    content = None
    doc_name = "{}.{}.json".format(serviceName, version)

    try:
        with open(os.path.join(DISCOVERY_DOC_DIR, doc_name), "r") as f:
            content = f.read()
    except FileNotFoundError:
        # File does not exist. Nothing to do here.
        pass

    return content
