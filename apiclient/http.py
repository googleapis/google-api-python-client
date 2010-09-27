# Copyright 2010 Google Inc. All Rights Reserved.

"""One-line documentation for http module.

A detailed description of http.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'


class HttpRequest(object):
  """Encapsulate an HTTP request.
  """

  def __init__(self, http, uri, method="GET", body=None, headers=None,
               postproc=None):
    self.uri = uri
    self.method = method
    self.body = body
    self.headers = headers or {}
    self.http = http
    self.postproc = postproc

  def execute(self, http=None):
    """Execute the request.

    If an http object is passed in it is used instead of the
    httplib2.Http object that the request was constructed with.
    """
    if http is None:
      http = self.http
    resp, content = http.request(self.uri, self.method,
                                      body=self.body,
                                      headers=self.headers)
    return self.postproc(resp, content)
