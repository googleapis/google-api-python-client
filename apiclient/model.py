#!/usr/bin/python2.4
#
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

"""Model objects for requests and responses.

Each API may support one or more serializations, such
as JSON, Atom, etc. The model classes are responsible
for converting between the wire format and the Python
object representation.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import gflags
import logging
import urllib

from anyjson import simplejson
from errors import HttpError

FLAGS = gflags.FLAGS

gflags.DEFINE_boolean('dump_request_response', False,
                     'Dump all http server requests and responses. '
                     'Must use apiclient.model.LoggingJsonModel as '
                     'the model.'
                     )


def _abstract():
  raise NotImplementedError('You need to override this function')


class Model(object):
  """Model base class.

  All Model classes should implement this interface.
  The Model serializes and de-serializes between a wire
  format such as JSON and a Python object representation.
  """

  def request(self, headers, path_params, query_params, body_value):
    """Updates outgoing requests with a deserialized body.

    Args:
      headers: dict, request headers
      path_params: dict, parameters that appear in the request path
      query_params: dict, parameters that appear in the query
      body_value: object, the request body as a Python object, which must be
                  serializable.
    Returns:
      A tuple of (headers, path_params, query, body)

      headers: dict, request headers
      path_params: dict, parameters that appear in the request path
      query: string, query part of the request URI
      body: string, the body serialized in the desired wire format.
    """
    _abstract()

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
    _abstract()


class JsonModel(Model):
  """Model class for JSON.

  Serializes and de-serializes between JSON and the Python
  object representation of HTTP request and response bodies.
  """

  def __init__(self, data_wrapper=False):
    """Construct a JsonModel

    Args:
      data_wrapper: boolean, wrap requests and responses in a data wrapper
    """
    self._data_wrapper = data_wrapper

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
    headers['accept-encoding'] = 'gzip, deflate'
    if 'user-agent' in headers:
      headers['user-agent'] += ' '
    else:
      headers['user-agent'] = ''
    headers['user-agent'] += 'google-api-python-client/1.0'

    if (isinstance(body_value, dict) and 'data' not in body_value and
        self._data_wrapper):
      body_value = {'data': body_value}
    if body_value is not None:
      headers['content-type'] = 'application/json'
      body_value = simplejson.dumps(body_value)
    return (headers, path_params, query, body_value)

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
      if type(value) == type([]):
        for x in value:
          x = x.encode('utf-8')
          astuples.append((key, x))
      else:
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


class LoggingJsonModel(JsonModel):
  """A printable JsonModel class that supports logging response info."""

  def response(self, resp, content):
    """An overloaded response method that will output debug info if requested.

    Args:
      resp: An httplib2.Response object.
      content: A string representing the response body.

    Returns:
      The body de-serialized as a Python object.
    """
    if FLAGS.dump_request_response:
      logging.info('--response-start--')
      for h, v in resp.iteritems():
        logging.info('%s: %s', h, v)
      if content:
        logging.info(content)
      logging.info('--response-end--')
    return super(LoggingJsonModel, self).response(
        resp, content)

  def request(self, headers, path_params, query_params, body_value):
    """An overloaded request method that will output debug info if requested.

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
    (headers, path_params, query, body) = super(
        LoggingJsonModel, self).request(
            headers, path_params, query_params, body_value)
    if FLAGS.dump_request_response:
      logging.info('--request-start--')
      logging.info('-headers-start-')
      for h, v in headers.iteritems():
        logging.info('%s: %s', h, v)
      logging.info('-headers-end-')
      logging.info('-path-parameters-start-')
      for h, v in path_params.iteritems():
        logging.info('%s: %s', h, v)
      logging.info('-path-parameters-end-')
      logging.info('body: %s', body)
      logging.info('query: %s', query)
      logging.info('--request-end--')
    return (headers, path_params, query, body)
