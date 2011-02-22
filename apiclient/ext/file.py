# Copyright 2010 Google Inc. All Rights Reserved.

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
