# Copyright 2010 Google Inc. All Rights Reserved.

"""Utilities for OAuth.

Utilities for making it easier to work with OAuth 1.0
credentials.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import pickle

from apiclient.oauth import Storage as BaseStorage


class Storage(BaseStorage):
  """Store and retrieve a single credential to and from a file."""

  def __init__(self, filename):
    self._filename = filename

  def get(self):
    """Retrieve Credential from file.

    Returns:
      apiclient.oauth.Credentials
    """
    try:
      f = open(self._filename, 'r')
      credentials = pickle.loads(f.read())
      f.close()
    except:
      credentials = None
    credentials.set_store(self.put)

    return credentials

  def put(self, credentials):
    """Write a pickled Credentials to file.

    Args:
      credentials: Credentials, the credentials to store.
    """
    f = open(self._filename, 'w')
    f.write(pickle.dumps(credentials))
    f.close()
