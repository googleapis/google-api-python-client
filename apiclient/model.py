#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Model objects for requests and responses

Each API may support one or more serializations, such
as JSON, Atom, etc. The model classes are responsible
for converting between the wire format and the Python
object representation.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import logging
import urllib

from anyjson import simplejson
from errors import HttpError


class JsonModel(object):
  """Model class for JSON.

  Serializes and de-serializes between JSON and the Python
  object representation of HTTP request and response bodies.
  """

  def request(self, headers, path_params, query_params, body_value):
    """Updates outgoing requests with JSON bodies.

    Args:
      headers: dict, request headers
      path_params: dict, parameters that appear in the request path
      query_params: dict, parameters that appear in the query
      body_value: object, the request body as a Python object, which must be
                  serializable by simplejson.
    Returns:
      A tuple of (headers, path_params, query, body)

      headers: dict, request headers
      path_params: dict, parameters that appear in the request path
      query: string, query part of the request URI
      body: string, the body serialized as JSON
    """
    query = self._build_query(query_params)
    headers['accept'] = 'application/json'
    if 'user-agent' in headers:
      headers['user-agent'] += ' '
    else:
      headers['user-agent'] = ''
    headers['user-agent'] += 'google-api-python-client/1.0'
    if body_value is None:
      return (headers, path_params, query, None)
    else:
      headers['content-type'] = 'application/json'
      return (headers, path_params, query, simplejson.dumps(body_value))

  def _build_query(self, params):
    """Builds a query string.

    Args:
      params: dict, the query parameters

    Returns:
      The query parameters properly encoded into an HTTP URI query string.
    """
    params.update({'alt': 'json'})
    astuples = []
    for key, value in params.iteritems():
      if getattr(value, 'encode', False) and callable(value.encode):
        value = value.encode('utf-8')
      astuples.append((key, value))
    return '?' + urllib.urlencode(astuples)

  def response(self, resp, content):
    """Convert the response wire format into a Python object.

    Args:
      resp: httplib2.Response, the HTTP response headers and status
      content: string, the body of the HTTP response

    Returns:
      The body de-serialized as a Python object.

    Raises:
      apiclient.errors.HttpError if a non 2xx response is received.
    """
    # Error handling is TBD, for example, do we retry
    # for some operation/error combinations?
    if resp.status < 300:
      if resp.status == 204:
        # A 204: No Content response should be treated differently
        # to all the other success states
        return simplejson.loads('{}')
      body = simplejson.loads(content)
      if isinstance(body, dict) and 'data' in body:
        body = body['data']
      return body
    else:
      logging.debug('Content from bad request was: %s' % content)
      raise HttpError(resp, content)
