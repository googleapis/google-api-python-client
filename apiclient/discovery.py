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
import re
import simplejson
import urlparse
import uritemplate


class HttpError(Exception):
  pass

DISCOVERY_URI = 'http://www.googleapis.com/discovery/0.1/describe\
{?api,apiVersion}'


def key2method(key):
  """
  max-results -> MaxResults
  """
  result = []
  key = list(key)
  newWord = True
  if not key[0].isalpha():
    result.append('X')
    newWord = False
  for c in key:
    if c.isalnum():
      if newWord:
        result.append(c.upper())
        newWord = False
      else:
        result.append(c.lower())
    else:
      newWord = True

  return ''.join(result)


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

  def request(self, headers, params):
    model = params.get('body', None)
    query = '?alt=json&prettyprint=true'
    headers['accept'] = 'application/json'
    if model == None:
      return (headers, params, query, None)
    else:
      model = {'data': model}
      headers['content-type'] = 'application/json'
      del params['body']
      return (headers, params, query, simplejson.dumps(model))

  def response(self, resp, content):
    # Error handling is TBD, for example, do we retry
    # for some operation/error combinations?
    if resp.status < 300:
      return simplejson.loads(content)['data']
    else:
      if resp['content-type'] != 'application/json':
        raise HttpError('%d %s' % (resp.status, resp.reason))
      else:
        raise HttpError(simplejson.loads(content)['error'])


def build(service, version, http=httplib2.Http(),
    discoveryServiceUrl=DISCOVERY_URI, auth=None, model=JsonModel()):
  params = {
      'api': service,
      'apiVersion': version
      }
  resp, content = http.request(uritemplate.expand(discoveryServiceUrl, params))
  d = simplejson.loads(content)
  service = d['data'][service][version]
  base = service['baseUrl']
  resources = service['resources']

  class Service(object):
    """Top level interface for a service"""

    def __init__(self, http=http):
      self._http = http
      self._baseUrl = base
      self._model = model

  def createMethod(theclass, methodName, methodDesc):

    def method(self, **kwargs):
      return createResource(self._http, self._baseUrl, self._model,
          methodName, methodDesc)

    setattr(method, '__doc__', 'A description of how to use this function')
    setattr(theclass, methodName, method)

  for methodName, methodDesc in resources.iteritems():
    createMethod(Service, methodName, methodDesc)
  return Service()


def createResource(http, baseUrl, model, resourceName, resourceDesc):

  class Resource(object):
    """A class for interacting with a resource."""

    def __init__(self):
      self._http = http
      self._baseUrl = baseUrl
      self._model = model

  def createMethod(theclass, methodName, methodDesc):
    pathUrl = methodDesc['pathUrl']
    pathUrl = re.sub(r'\{', r'{+', pathUrl)
    httpMethod = methodDesc['httpMethod']
    args = methodDesc['parameters'].keys()

    required = [] # Required parameters
    pattern = {}  # Parameters the must match a regex
    for arg, desc in methodDesc['parameters'].iteritems():
      param = key2param(arg)
      if desc.get('pattern', ''):
        pattern[param] = desc['pattern']
      if desc.get('required', False):
        required.append(param)

    if httpMethod in ['PUT', 'POST']:
      args.append('body')
    argmap = dict([(key2param(key), key) for key in args])

    def method(self, **kwargs):
      for name in kwargs.iterkeys():
        if name not in argmap:
          raise TypeError('Got an unexpected keyword argument "%s"' % name)

      for name in required:
        if name not in kwargs:
          raise TypeError('Missing required parameter "%s"' % name)

      for name, regex in pattern.iteritems():
        if name in kwargs:
          if re.match(regex, kwargs[name]) is None:
            raise TypeError('Parameter "%s" value "%s" does not match the pattern "%s"' % (name, kwargs[name], regex))

      params = {}
      for key, value in kwargs.iteritems():
        params[argmap[key]] = value

      headers = {}
      headers, params, query, body = self._model.request(headers, params)

      url = urlparse.urljoin(self._baseUrl,
          uritemplate.expand(pathUrl, params) + query)

      resp, content = self._http.request(
          url, method=httpMethod, headers=headers, body=body)

      return self._model.response(resp, content)

    docs = ['A description of how to use this function\n\n']
    for arg in argmap.iterkeys():
      docs.append('%s - A parameter\n' % arg)

    setattr(method, '__doc__', ''.join(docs))
    setattr(theclass, methodName, method)

  for methodName, methodDesc in resourceDesc['methods'].iteritems():
    createMethod(Resource, methodName, methodDesc)

  return Resource()
