#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Utilities for OAuth.

Utilities for making it easier to work with OAuth.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import copy
import httplib2
import oauth2 as oauth
import urllib
import logging

try:
    from urlparse import parse_qs, parse_qsl
except ImportError:
    from cgi import parse_qs, parse_qsl


class Error(Exception):
  """Base error for this module."""
  pass


class RequestError(Error):
  """Error occurred during request."""
  pass


class MissingParameter(Error):
  pass


def _abstract():
  raise NotImplementedError('You need to override this function')


def _oauth_uri(name, discovery, params):
  """Look up the OAuth UR from the discovery
  document and add query parameters based on
  params.

  name      - The name of the OAuth URI to lookup, one
              of 'request', 'access', or 'authorize'.
  discovery - Portion of discovery document the describes
              the OAuth endpoints.
  params    - Dictionary that is used to form the query parameters
              for the specified URI.
  """
  if name not in ['request', 'access', 'authorize']:
    raise KeyError(name)
  keys = discovery[name]['parameters'].keys()
  query = {}
  for key in keys:
    if key in params:
      query[key] = params[key]
  return discovery[name]['url'] + '?' + urllib.urlencode(query)


class Credentials(object):
  """Base class for all Credentials objects.

  Subclasses must define an authorize() method
  that applies the credentials to an HTTP transport.
  """

  def authorize(self, http):
    """Take an httplib2.Http instance (or equivalent) and
    authorizes it for the set of credentials, usually by
    replacing http.request() with a method that adds in
    the appropriate headers and then delegates to the original
    Http.request() method.
    """
    _abstract()


class OAuthCredentials(Credentials):
  """Credentials object for OAuth 1.0a
  """

  def __init__(self, consumer, token, user_agent):
    """
    consumer   - An instance of oauth.Consumer.
    token      - An instance of oauth.Token constructed with
                 the access token and secret.
    user_agent - The HTTP User-Agent to provide for this application.
    """
    self.consumer = consumer
    self.token = token
    self.user_agent = user_agent

  def authorize(self, http):
    """
    Args:
       http - An instance of httplib2.Http
           or something that acts like it.

    Returns:
       A modified instance of http that was passed in.

    Example:

      h = httplib2.Http()
      h = credentials.authorize(h)

    You can't create a new OAuth
    subclass of httplib2.Authenication because
    it never gets passed the absolute URI, which is
    needed for signing. So instead we have to overload
    'request' with a closure that adds in the
    Authorization header and then calls the original version
    of 'request()'.
    """
    request_orig = http.request
    signer = oauth.SignatureMethod_HMAC_SHA1()

    # The closure that will replace 'httplib2.Http.request'.
    def new_request(uri, method='GET', body=None, headers=None,
                    redirections=httplib2.DEFAULT_MAX_REDIRECTS,
                    connection_type=None):
      """Modify the request headers to add the appropriate
      Authorization header."""
      req = oauth.Request.from_consumer_and_token(
          self.consumer, self.token, http_method=method, http_url=uri)
      req.sign_request(signer, self.consumer, self.token)
      if headers == None:
        headers = {}
      headers.update(req.to_header())
      if 'user-agent' in headers:
        headers['user-agent'] =  self.user_agent + ' ' + headers['user-agent']
      else:
        headers['user-agent'] =  self.user_agent
      return request_orig(uri, method, body, headers,
                          redirections, connection_type)

    http.request = new_request
    return http


class FlowThreeLegged(object):
  """Does the Three Legged Dance for OAuth 1.0a.
  """

  def __init__(self, discovery, consumer_key, consumer_secret, user_agent,
               **kwargs):
    """
    discovery       - Section of the API discovery document that describes
                      the OAuth endpoints.
    consumer_key    - OAuth consumer key
    consumer_secret - OAuth consumer secret
    user_agent      - The HTTP User-Agent that identifies the application.
    **kwargs        - The keyword arguments are all optional and required
                      parameters for the OAuth calls.
    """
    self.discovery = discovery
    self.consumer_key = consumer_key
    self.consumer_secret = consumer_secret
    self.user_agent = user_agent
    self.params = kwargs
    self.request_token = {}
    required = {}
    for uriinfo in discovery.itervalues():
      for name, value in uriinfo['parameters'].iteritems():
        if value['required'] and not name.startswith('oauth_'):
          required[name] = 1
    for key in required.iterkeys():
      if key not in self.params:
        raise MissingParameter('Required parameter %s not supplied' % key)

  def step1_get_authorize_url(self, oauth_callback='oob'):
    """Returns a URI to redirect to the provider.

    oauth_callback - Either the string 'oob' for a non-web-based application,
                     or a URI that handles the callback from the authorization
                     server.

    If oauth_callback is 'oob' then pass in the
    generated verification code to step2_exchange,
    otherwise pass in the query parameters received
    at the callback uri to step2_exchange.
    """
    consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
    client = oauth.Client(consumer)

    headers = {
        'user-agent': self.user_agent,
        'content-type': 'application/x-www-form-urlencoded'
    }
    body = urllib.urlencode({'oauth_callback': oauth_callback})
    uri = _oauth_uri('request', self.discovery, self.params)

    resp, content = client.request(uri, 'POST', headers=headers,
                                   body=body)
    if resp['status'] != '200':
      logging.error('Failed to retrieve temporary authorization: %s' % content)
      raise RequestError('Invalid response %s.' % resp['status'])

    self.request_token = dict(parse_qsl(content))

    auth_params = copy.copy(self.params)
    auth_params['oauth_token'] = self.request_token['oauth_token']

    return _oauth_uri('authorize', self.discovery, auth_params)

  def step2_exchange(self, verifier):
    """Exhanges an authorized request token
    for OAuthCredentials.

    verifier - either the verifier token, or a dictionary
        of the query parameters to the callback, which contains
        the oauth_verifier.
    """

    if not (isinstance(verifier, str) or isinstance(verifier, unicode)):
      verifier = verifier['oauth_verifier']

    token = oauth.Token(
        self.request_token['oauth_token'],
        self.request_token['oauth_token_secret'])
    token.set_verifier(verifier)
    consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
    client = oauth.Client(consumer, token)

    headers = {
        'user-agent': self.user_agent,
        'content-type': 'application/x-www-form-urlencoded'
    }

    uri = _oauth_uri('access', self.discovery, self.params)
    resp, content = client.request(uri, 'POST', headers=headers)
    if resp['status'] != '200':
      logging.error('Failed to retrieve access token: %s' % content)
      raise RequestError('Invalid response %s.' % resp['status'])

    oauth_params = dict(parse_qsl(content))
    token = oauth.Token(
        oauth_params['oauth_token'],
        oauth_params['oauth_token_secret'])

    return OAuthCredentials(consumer, token, self.user_agent)
