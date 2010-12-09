#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""One-line documentation for util module.

A detailed description of util.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import httplib2
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class HttpMock(object):

  def __init__(self, filename, headers):
    f = file(os.path.join(DATA_DIR, filename), 'r')
    self.data = f.read()
    f.close()
    self.headers = headers

  def request(self, uri, method="GET", body=None, headers=None, redirections=1, connection_type=None):
    return httplib2.Response(self.headers), self.data
