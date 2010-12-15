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
import uritemplate
import urllib
import urlparse
try:
    from urlparse import parse_qsl
except ImportError:
    from cgi import parse_qsl

from http import HttpRequest
from anyjson import simplejson
from model import JsonModel
from errors import HttpError
from errors import UnknownLinkType

URITEMPLATE = re.compile('{[^}]*}')
VARNAME = re.compile('[a-zA-Z0-9_-]+')
DISCOVERY_URI = ('https://www.googleapis.com/discovery/v0.2beta1/describe/'
  '{api}/{apiVersion}')


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


def build(serviceName, version,
    http=None,
    discoveryServiceUrl=DISCOVERY_URI,
    developerKey=None,
    model=JsonModel(),
    requestBuilder=HttpRequest):
  params = {
      'api': serviceName,
      'apiVersion': version
      }

  if http is None:
    http = httplib2.Http()
  requested_url = uritemplate.expand(discoveryServiceUrl, params)
  logging.info('URL being requested: %s' % requested_url)
  resp, content = http.request(requested_url)
  service = simplejson.loads(content)

  fn = os.path.join(os.path.dirname(__file__), "contrib",
      serviceName, "future.json")
  try:
    f = file(fn, "r")
    d = simplejson.load(f)
    f.close()
    future = d['resources']
    auth_discovery = d['auth']
  except IOError:
    future = {}
    auth_discovery = {}

  base = urlparse.urljoin(discoveryServiceUrl, service['restBasePath'])
  resources = service['resources']

  class Service(object):
    """Top level interface for a service"""

    def __init__(self, http=http):
      self._http = http
      self._baseUrl = base
      self._model = model
      self._developerKey = developerKey
      self._requestBuilder = requestBuilder

    def auth_discovery(self):
      return auth_discovery

  def createMethod(theclass, methodName, methodDesc, futureDesc):

    def method(self):
      return createResource(self._http, self._baseUrl, self._model,
                            self._requestBuilder, methodName,
                            self._developerKey, methodDesc, futureDesc)

    setattr(method, '__doc__', 'A description of how to use this function')
    setattr(method, '__is_resource__', True)
    setattr(theclass, methodName, method)

  for methodName, methodDesc in resources.iteritems():
    createMethod(Service, methodName, methodDesc, future.get(methodName, {}))
  return Service()


def createResource(http, baseUrl, model, requestBuilder, resourceName,
                   developerKey, resourceDesc, futureDesc):

  class Resource(object):
    """A class for interacting with a resource."""

    def __init__(self):
      self._http = http
      self._baseUrl = baseUrl
      self._model = model
      self._developerKey = developerKey
      self._requestBuilder = requestBuilder

  def createMethod(theclass, methodName, methodDesc, futureDesc):
    pathUrl = methodDesc['restPath']
    pathUrl = re.sub(r'\{', r'{+', pathUrl)
    httpMethod = methodDesc['httpMethod']
    methodId = methodDesc['rpcMethod']

    argmap = {}
    if httpMethod in ['PUT', 'POST']:
      argmap['body'] = 'body'


    required_params = [] # Required parameters
    pattern_params = {}  # Parameters that must match a regex
    query_params = [] # Parameters that will be used in the query string
    path_params = {} # Parameters that will be used in the base URL
    if 'parameters' in methodDesc:
      for arg, desc in methodDesc['parameters'].iteritems():
        param = key2param(arg)
        argmap[param] = arg

        if desc.get('pattern', ''):
          pattern_params[param] = desc['pattern']
        if desc.get('required', False):
          required_params.append(param)
        if desc.get('restParameterType') == 'query':
          query_params.append(param)
        if desc.get('restParameterType') == 'path':
          path_params[param] = param

    for match in URITEMPLATE.finditer(pathUrl):
      for namematch in VARNAME.finditer(match.group(0)):
        name = key2param(namematch.group(0))
        path_params[name] = name
        if name in query_params:
          query_params.remove(name)

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

      if self._developerKey:
        actual_query_params['key'] = self._developerKey

      headers = {}
      headers, params, query, body = self._model.request(headers,
          actual_path_params, actual_query_params, body_value)

      # TODO(ade) This exists to fix a bug in V1 of the Buzz discovery
      # document.  Base URLs should not contain any path elements. If they do
      # then urlparse.urljoin will strip them out This results in an incorrect
      # URL which returns a 404
      url_result = urlparse.urlsplit(self._baseUrl)
      new_base_url = url_result.scheme + '://' + url_result.netloc

      expanded_url = uritemplate.expand(pathUrl, params)
      url = urlparse.urljoin(new_base_url,
                             url_result.path + expanded_url + query)

      logging.info('URL being requested: %s' % url)
      return self._requestBuilder(self._http, url,
                                  method=httpMethod, body=body,
                                  headers=headers,
                                  postproc=self._model.response,
                                  methodId=methodId)

    docs = ['A description of how to use this function\n\n']
    for arg in argmap.iterkeys():
      required = ""
      if arg in required_params:
        required = " (required)"
      docs.append('%s - A parameter%s\n' % (arg, required))

    setattr(method, '__doc__', ''.join(docs))
    setattr(theclass, methodName, method)

  def createNextMethod(theclass, methodName, methodDesc, futureDesc):
    methodId = methodDesc['rpcMethod'] + '.next'

    def method(self, previous):
      """
      Takes a single argument, 'body', which is the results
      from the last call, and returns the next set of items
      in the collection.

      Returns None if there are no more items in
      the collection.
      """
      if futureDesc['type'] != 'uri':
        raise UnknownLinkType(futureDesc['type'])

      try:
        p = previous
        for key in futureDesc['location']:
          p = p[key]
        url = p
      except (KeyError, TypeError):
        return None

      if self._developerKey:
        parsed = list(urlparse.urlparse(url))
        q = parse_qsl(parsed[4])
        q.append(('key', self._developerKey))
        parsed[4] = urllib.urlencode(q)
        url = urlparse.urlunparse(parsed)

      headers = {}
      headers, params, query, body = self._model.request(headers, {}, {}, None)

      logging.info('URL being requested: %s' % url)
      resp, content = self._http.request(url, method='GET', headers=headers)

      return self._requestBuilder(self._http, url, method='GET',
                                  headers=headers,
                                  postproc=self._model.response,
                                  methodId=methodId)

    setattr(theclass, methodName, method)

  # Add basic methods to Resource
  if 'methods' in resourceDesc:
    for methodName, methodDesc in resourceDesc['methods'].iteritems():
      if futureDesc:
        future = futureDesc['methods'].get(methodName, {})
      else:
        future = None
      createMethod(Resource, methodName, methodDesc, future)

  # Add in nested resources
  if 'resources' in resourceDesc:

    def createMethod(theclass, methodName, methodDesc, futureDesc):

      def method(self):
        return createResource(self._http, self._baseUrl, self._model,
            methodName, self._developerKey, methodDesc, futureDesc)

      setattr(method, '__doc__', 'A description of how to use this function')
      setattr(method, '__is_resource__', True)
      setattr(theclass, methodName, method)

    for methodName, methodDesc in resourceDesc['resources'].iteritems():
      if futureDesc and 'resources' in futureDesc:
        future = futureDesc['resources'].get(methodName, {})
      else:
        future = {}
      createMethod(Resource, methodName, methodDesc,
                   future.get(methodName, {}))

  # Add <m>_next() methods to Resource
  if futureDesc:
    for methodName, methodDesc in futureDesc['methods'].iteritems():
      if 'next' in methodDesc and methodName in resourceDesc['methods']:
        createNextMethod(Resource, methodName + "_next",
                         resourceDesc['methods'][methodName],
                         methodDesc['next'])

  return Resource()
