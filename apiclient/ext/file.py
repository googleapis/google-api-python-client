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

Utilities for making it easier to work with OAuth 1.0 credentials.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import pickle
import threading

from apiclient.oauth import Storage as BaseStorage


class Storage(BaseStorage):
  """Store and retrieve a single credential to and from a file."""

  def __init__(self, filename):
    self._filename = filename
    self._lock = threading.Lock()

  def get(self):
    """Retrieve Credential from file.

    Returns:
      apiclient.oauth.Credentials
    """
    self._lock.acquire()
    try:
      f = open(self._filename, 'r')
      credentials = pickle.loads(f.read())
      f.close()
      credentials.set_store(self.put)
    except:
      credentials = None
    self._lock.release()

    return credentials

  def put(self, credentials):
    """Write a pickled Credentials to file.

    Args:
      credentials: Credentials, the credentials to store.
    """
    self._lock.acquire()
    f = open(self._filename, 'w')
    f.write(pickle.dumps(credentials))
    f.close()
    self._lock.release()
