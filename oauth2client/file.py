# Copyright (C) 2010 Google Inc.
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

"""Utilities for OAuth.

Utilities for making it easier to work with OAuth 2.0
credentials.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import threading


try:  # pragma: no cover
  import simplejson
except ImportError:  # pragma: no cover
  try:
    # Try to import from django, should work on App Engine
    from django.utils import simplejson
  except ImportError:
    # Should work for Python2.6 and higher.
    import json as simplejson


from client import Storage as BaseStorage
from client import Credentials


class Storage(BaseStorage):
  """Store and retrieve a single credential to and from a file."""

  def __init__(self, filename):
    self._filename = filename
    self._lock = threading.Lock()

  def acquire_lock(self):
    """Acquires any lock necessary to access this Storage.

    This lock is not reentrant."""
    self._lock.acquire()

  def release_lock(self):
    """Release the Storage lock.

    Trying to release a lock that isn't held will result in a
    RuntimeError.
    """
    self._lock.release()

  def locked_get(self):
    """Retrieve Credential from file.

    Returns:
      oauth2client.client.Credentials
    """
    credentials = None
    try:
      f = open(self._filename, 'r')
      content = f.read()
      f.close()
    except IOError:
      return credentials

    try:
      credentials = Credentials.new_from_json(content)
      credentials.set_store(self)
    except ValueError:
      pass

    return credentials

  def locked_put(self, credentials):
    """Write Credentials to file.

    Args:
      credentials: Credentials, the credentials to store.
    """
    f = open(self._filename, 'w')
    f.write(credentials.to_json())
    f.close()
