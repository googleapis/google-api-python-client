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

A client library for Google's discovery based APIs.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'
__all__ = [
    'build', 'build_from_document'
    ]

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
from errors import UnknownLinkType
from errors import HttpError
from errors import InvalidJsonError

URITEMPLATE = re.compile('{[^}]*}')
VARNAME = re.compile('[a-zA-Z0-9_-]+')
DISCOVERY_URI = ('https://www.googleapis.com/discovery/v1/apis/'
  '{api}/{apiVersion}/rest')
DEFAULT_METHOD_DOC = 'A description of how to use this function'

# Query parameters that work, but don't appear in discovery
STACK_QUERY_PARAMETERS = ['trace', 'fields', 'pp', 'prettyPrint', 'userIp',
  'strict']


def key2param(key):
  """Converts key names into parameter names.

  For example, converting "max-results" -> "max_results"
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
          model=None,
          requestBuilder=HttpRequest):
  """Construct a Resource for interacting with an API.

  Construct a Resource object for interacting with
  an API. The serviceName and version are the
  names from the Discovery service.

  Args:
    serviceName: string, name of the service
    version: string, the version of the service
    discoveryServiceUrl: string, a URI Template that points to
      the location of the discovery service. It should have two
      parameters {api} and {apiVersion} that when filled in
      produce an absolute URI to the discovery document for
      that service.
    developerKey: string, key obtained
      from https://code.google.com/apis/console
    model: apiclient.Model, converts to and from the wire format
    requestBuilder: apiclient.http.HttpRequest, encapsulator for
      an HTTP request

  Returns:
    A Resource object with methods for interacting with
    the service.
  """
  params = {
      'api': serviceName,
      'apiVersion': version
      }

  if http is None:
    http = httplib2.Http()
  requested_url = uritemplate.expand(discoveryServiceUrl, params)
  logging.info('URL being requested: %s' % requested_url)
  resp, content = http.request(requested_url)
  if resp.status > 400:
    raise HttpError(resp, content, requested_url)
  try:
    service = simplejson.loads(content)
  except ValueError, e:
    logging.error('Failed to parse as JSON: ' + content)
    raise InvalidJsonError()

  fn = os.path.join(os.path.dirname(__file__), 'contrib',
      serviceName, 'future.json')
  try:
    f = file(fn, 'r')
    future = f.read()
    f.close()
  except IOError:
    future = None

  return build_from_document(content, discoveryServiceUrl, future,
      http, developerKey, model, requestBuilder)


def build_from_document(
    service,
    base,
    future=None,
    http=None,
    developerKey=None,
    model=None,
    requestBuilder=HttpRequest):
  """Create a Resource for interacting with an API.

  Same as `build()`, but constructs the Resource object
  from a discovery document that is it given, as opposed to
  retrieving one over HTTP.

  Args:
    service: string, discovery document
    base: string, base URI for all HTTP requests, usually the discovery URI
    future: string, discovery document with future capabilities
    auth_discovery: dict, information about the authentication the API supports
    http: httplib2.Http, An instance of httplib2.Http or something that acts
      like it that HTTP requests will be made through.
    developerKey: string, Key for controlling API usage, generated
      from the API Console.
    model: Model class instance that serializes and
      de-serializes requests and responses.
    requestBuilder: Takes an http request and packages it up to be executed.

  Returns:
    A Resource object with methods for interacting with
    the service.
  """

  service = simplejson.loads(service)
  base = urlparse.urljoin(base, service['basePath'])
  if future:
    future = simplejson.loads(future)
    auth_discovery = future.get('auth', {})
  else:
    future = {}
    auth_discovery = {}

  if model is None:
    features = service.get('features', [])
    model = JsonModel('dataWrapper' in features)
  resource = createResource(http, base, model, requestBuilder, developerKey,
                       service, future)

  def auth_method():
    """Discovery information about the authentication the API uses."""
    return auth_discovery

  setattr(resource, 'auth_discovery', auth_method)

  return resource


def _cast(value, schema_type):
  """Convert value to a string based on JSON Schema type.

  See http://tools.ietf.org/html/draft-zyp-json-schema-03 for more details on
  JSON Schema.

  Args:
    value: any, the value to convert
    schema_type: string, the type that value should be interpreted as

  Returns:
    A string representation of 'value' based on the schema_type.
  """
  if schema_type == 'string':
    if type(value) == type('') or type(value) == type(u''):
      return value
    else:
      return str(value)
  elif schema_type == 'integer':
    return str(int(value))
  elif schema_type == 'number':
    return str(float(value))
  elif schema_type == 'boolean':
    return str(bool(value)).lower()
  else:
    if type(value) == type('') or type(value) == type(u''):
      return value
    else:
      return str(value)


def createResource(http, baseUrl, model, requestBuilder,
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
    pathUrl = methodDesc['path']
    httpMethod = methodDesc['httpMethod']
    methodId = methodDesc['id']

    if 'parameters' not in methodDesc:
      methodDesc['parameters'] = {}
    for name in STACK_QUERY_PARAMETERS:
      methodDesc['parameters'][name] = {
          'type': 'string',
          'location': 'query'
          }

    if httpMethod in ['PUT', 'POST', 'PATCH']:
      methodDesc['parameters']['body'] = {
          'description': 'The request body.',
          'type': 'object',
          'required': True,
          }

    argmap = {} # Map from method parameter name to query parameter name
    required_params = [] # Required parameters
    repeated_params = [] # Repeated parameters
    pattern_params = {}  # Parameters that must match a regex
    query_params = [] # Parameters that will be used in the query string
    path_params = {} # Parameters that will be used in the base URL
    param_type = {} # The type of the parameter
    enum_params = {} # Allowable enumeration values for each parameter


    if 'parameters' in methodDesc:
      for arg, desc in methodDesc['parameters'].iteritems():
        param = key2param(arg)
        argmap[param] = arg

        if desc.get('pattern', ''):
          pattern_params[param] = desc['pattern']
        if desc.get('enum', ''):
          enum_params[param] = desc['enum']
        if desc.get('required', False):
          required_params.append(param)
        if desc.get('repeated', False):
          repeated_params.append(param)
        if desc.get('location') == 'query':
          query_params.append(param)
        if desc.get('location') == 'path':
          path_params[param] = param
        param_type[param] = desc.get('type', 'string')

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

      for name, enums in enum_params.iteritems():
        if name in kwargs:
          if kwargs[name] not in enums:
            raise TypeError(
                'Parameter "%s" value "%s" is not an allowed value in "%s"' %
                (name, kwargs[name], str(enums)))

      actual_query_params = {}
      actual_path_params = {}
      for key, value in kwargs.iteritems():
        to_type = param_type.get(key, 'string')
        # For repeated parameters we cast each member of the list.
        if key in repeated_params and type(value) == type([]):
          cast_value = [_cast(x, to_type) for x in value]
        else:
          cast_value = _cast(value, to_type)
        if key in query_params:
          actual_query_params[argmap[key]] = cast_value
        if key in path_params:
          actual_path_params[argmap[key]] = cast_value
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
      new_base_url = url_result[0] + '://' + url_result[1]

      expanded_url = uritemplate.expand(pathUrl, params)
      url = urlparse.urljoin(self._baseUrl,
                             url_result[2] + expanded_url + query)

      logging.info('URL being requested: %s' % url)
      return self._requestBuilder(self._http,
                                  self._model.response,
                                  url,
                                  method=httpMethod,
                                  body=body,
                                  headers=headers,
                                  methodId=methodId)

    docs = [methodDesc.get('description', DEFAULT_METHOD_DOC), '\n\n']
    if len(argmap) > 0:
      docs.append('Args:\n')
    for arg in argmap.iterkeys():
      if arg in STACK_QUERY_PARAMETERS:
        continue
      repeated = ''
      if arg in repeated_params:
        repeated = ' (repeated)'
      required = ''
      if arg in required_params:
        required = ' (required)'
      paramdesc = methodDesc['parameters'][argmap[arg]]
      paramdoc = paramdesc.get('description', 'A parameter')
      paramtype = paramdesc.get('type', 'string')
      docs.append('  %s: %s, %s%s%s\n' % (arg, paramtype, paramdoc, required,
                                          repeated))
      enum = paramdesc.get('enum', [])
      enumDesc = paramdesc.get('enumDescriptions', [])
      if enum and enumDesc:
        docs.append('    Allowed values\n')
        for (name, desc) in zip(enum, enumDesc):
          docs.append('      %s - %s\n' % (name, desc))

    setattr(method, '__doc__', ''.join(docs))
    setattr(theclass, methodName, method)

  def createNextMethod(theclass, methodName, methodDesc, futureDesc):
    methodId = methodDesc['id'] + '.next'

    def methodNext(self, previous):
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

      return self._requestBuilder(self._http,
                                  self._model.response,
                                  url,
                                  method='GET',
                                  headers=headers,
                                  methodId=methodId)

    setattr(theclass, methodName, methodNext)

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

    def createResourceMethod(theclass, methodName, methodDesc, futureDesc):

      def methodResource(self):
        return createResource(self._http, self._baseUrl, self._model,
                              self._requestBuilder, self._developerKey,
                              methodDesc, futureDesc)

      setattr(methodResource, '__doc__', 'A collection resource.')
      setattr(methodResource, '__is_resource__', True)
      setattr(theclass, methodName, methodResource)

    for methodName, methodDesc in resourceDesc['resources'].iteritems():
      if futureDesc and 'resources' in futureDesc:
        future = futureDesc['resources'].get(methodName, {})
      else:
        future = {}
      createResourceMethod(Resource, methodName, methodDesc, future)

  # Add <m>_next() methods to Resource
  if futureDesc and 'methods' in futureDesc:
    for methodName, methodDesc in futureDesc['methods'].iteritems():
      if 'next' in methodDesc and methodName in resourceDesc['methods']:
        createNextMethod(Resource, methodName + '_next',
                         resourceDesc['methods'][methodName],
                         methodDesc['next'])

  return Resource()
