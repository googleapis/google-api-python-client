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

"""Client for discovery based APIs

A client library for Google's discovery
based APIs.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'


import httplib2
import logging
import os
import re
import simplejson
import uritemplate
import urllib
import urlparse


class HttpError(Exception):
  pass


class UnknownLinkType(Exception):
  pass

DISCOVERY_URI = ('http://www.googleapis.com/discovery/0.1/describe'
  '{?api,apiVersion}')


def key2param(key):
  """
  max-results -> max_results
  """
  result = []
  key = list(key)
  if not key[0].isalpha():
    result.append('x')
  for c in key:
    if c.isalnum():
      result.append(c)
    else:
      result.append('_')

  return ''.join(result)


class JsonModel(object):

  def request(self, headers, path_params, query_params, body_value):
    query = self.build_query(query_params)
    headers['accept'] = 'application/json'
    if body_value is None:
      return (headers, path_params, query, None)
    else:
      model = {'data': body_value}
      headers['content-type'] = 'application/json'
      return (headers, path_params, query, simplejson.dumps(model))

  def build_query(self, params):
    params.update({'alt': 'json', 'prettyprint': 'true'})
    astuples = []
    for key, value in params.iteritems():
      if getattr(value, 'encode', False) and callable(value.encode):
        value = value.encode('utf-8')
      astuples.append((key, value))
    return '?' + urllib.urlencode(astuples)

  def response(self, resp, content):
    # Error handling is TBD, for example, do we retry
    # for some operation/error combinations?
    if resp.status < 300:
      return simplejson.loads(content)['data']
    else:
      logging.debug('Content from bad request was: %s' % content)
      if resp['content-type'] != 'application/json':
        raise HttpError('%d %s' % (resp.status, resp.reason))
      else:
        raise HttpError(simplejson.loads(content)['error'])


def build(serviceName, version, http=httplib2.Http(),
    discoveryServiceUrl=DISCOVERY_URI, auth=None, model=JsonModel()):
  params = {
      'api': serviceName,
      'apiVersion': version
      }

  requested_url = uritemplate.expand(discoveryServiceUrl, params)
  logging.info('URL being requested: %s' % requested_url)
  resp, content = http.request(requested_url)
  d = simplejson.loads(content)
  service = d['data'][serviceName][version]

  fn = os.path.join(os.path.dirname(__file__), "contrib",
      serviceName, "future.json")
  f = file(fn, "r")
  d = simplejson.load(f)
  f.close()
  future = d['data'][serviceName][version]['resources']

  base = service['baseUrl']
  resources = service['resources']

  class Service(object):
    """Top level interface for a service"""

    def __init__(self, http=http):
      self._http = http
      self._baseUrl = base
      self._model = model

  def createMethod(theclass, methodName, methodDesc, futureDesc):

    def method(self, **kwargs):
      return createResource(self._http, self._baseUrl, self._model,
          methodName, methodDesc, futureDesc)

    setattr(method, '__doc__', 'A description of how to use this function')
    setattr(theclass, methodName, method)

  for methodName, methodDesc in resources.iteritems():
    createMethod(Service, methodName, methodDesc, future[methodName])
  return Service()


def createResource(http, baseUrl, model, resourceName, resourceDesc,
    futureDesc):

  class Resource(object):
    """A class for interacting with a resource."""

    def __init__(self):
      self._http = http
      self._baseUrl = baseUrl
      self._model = model

  def createMethod(theclass, methodName, methodDesc, futureDesc):
    pathUrl = methodDesc['pathUrl']
    pathUrl = re.sub(r'\{', r'{+', pathUrl)
    httpMethod = methodDesc['httpMethod']

    argmap = {}
    if httpMethod in ['PUT', 'POST']:
      argmap['body'] = 'body'


    required_params = [] # Required parameters
    pattern_params = {}  # Parameters that must match a regex
    query_params = [] # Parameters that will be used in the query string
    path_params = {} # Parameters that will be used in the base URL
    for arg, desc in methodDesc['parameters'].iteritems():
      param = key2param(arg)
      argmap[param] = arg

      if desc.get('pattern', ''):
        pattern_params[param] = desc['pattern']
      if desc.get('required', False):
        required_params.append(param)
      if desc.get('parameterType') == 'query':
        query_params.append(param)
      if desc.get('parameterType') == 'path':
        path_params[param] = param

    def method(self, **kwargs):
      for name in kwargs.iterkeys():
        if name not in argmap:
          raise TypeError('Got an unexpected keyword argument "%s"' % name)

      for name in required_params:
        if name not in kwargs:
          raise TypeError('Missing required parameter "%s"' % name)

      for name, regex in pattern_params.iteritems():
        if name in kwargs:
          if re.match(regex, kwargs[name]) is None:
            raise TypeError(
                'Parameter "%s" value "%s" does not match the pattern "%s"' %
                (name, kwargs[name], regex))

      actual_query_params = {}
      actual_path_params = {}
      for key, value in kwargs.iteritems():
        if key in query_params:
          actual_query_params[argmap[key]] = value
        if key in path_params:
          actual_path_params[argmap[key]] = value
      body_value = kwargs.get('body', None)

      headers = {}
      headers, params, query, body = self._model.request(headers,
          actual_path_params, actual_query_params, body_value)

      expanded_url = uritemplate.expand(pathUrl, params)
      url = urlparse.urljoin(self._baseUrl, expanded_url + query)

      logging.info('URL being requested: %s' % url)
      resp, content = self._http.request(
          url, method=httpMethod, headers=headers, body=body)

      return self._model.response(resp, content)

    docs = ['A description of how to use this function\n\n']
    for arg in argmap.iterkeys():
      required = ""
      if arg in required_params:
        required = " (required)"
      docs.append('%s - A parameter%s\n' % (arg, required))

    setattr(method, '__doc__', ''.join(docs))
    setattr(theclass, methodName, method)

  def createNextMethod(theclass, methodName, methodDesc):

    def method(self, previous):
      """
      Takes a single argument, 'body', which is the results
      from the last call, and returns the next set of items
      in the collection.

      Returns None if there are no more items in
      the collection.
      """
      if methodDesc['type'] != 'uri':
        raise UnknownLinkType(methodDesc['type'])

      try:
        p = previous
        for key in methodDesc['location']:
          p = p[key]
        url = p
      except KeyError:
        return None

      headers = {}
      headers, params, query, body = self._model.request(headers, {}, {}, None)

      logging.info('URL being requested: %s' % url)
      resp, content = self._http.request(url, method='GET', headers=headers)

      return self._model.response(resp, content)

    setattr(theclass, methodName, method)

  # Add basic methods to Resource
  for methodName, methodDesc in resourceDesc['methods'].iteritems():
    future = futureDesc['methods'].get(methodName, {})
    createMethod(Resource, methodName, methodDesc, future)

  # Add <m>_next() methods to Resource
  for methodName, methodDesc in futureDesc['methods'].iteritems():
    if 'next' in methodDesc and methodName in resourceDesc['methods']:
      createNextMethod(Resource, methodName + "_next", methodDesc['next'])

  return Resource()
