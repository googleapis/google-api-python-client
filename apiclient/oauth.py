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

"""Utilities for OAuth.

Utilities for making it easier to work with OAuth.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'


import copy
import httplib2
import logging
import oauth2 as oauth
import urllib
import urlparse
from anyjson import simplejson

try:
  from urlparse import parse_qsl
except ImportError:
  from cgi import parse_qsl


class Error(Exception):
  """Base error for this module."""
  pass


class RequestError(Error):
  """Error occurred during request."""
  pass


class MissingParameter(Error):
  pass


class CredentialsInvalidError(Error):
  pass


def _abstract():
  raise NotImplementedError('You need to override this function')


def _oauth_uri(name, discovery, params):
  """Look up the OAuth URI from the discovery
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


class Flow(object):
  """Base class for all Flow objects."""
  pass


class Storage(object):
  """Base class for all Storage objects.

  Store and retrieve a single credential.
  """

  def get(self):
    """Retrieve credential.

    Returns:
      apiclient.oauth.Credentials
    """
    _abstract()

  def put(self, credentials):
    """Write a credential.

    Args:
      credentials: Credentials, the credentials to store.
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
    self.store = None

    # True if the credentials have been revoked
    self._invalid = False

  @property
  def invalid(self):
    """True if the credentials are invalid, such as being revoked."""
    return getattr(self, "_invalid", False)

  def set_store(self, store):
    """Set the storage for the credential.

    Args:
      store: callable, a callable that when passed a Credential
        will store the credential back to where it came from.
        This is needed to store the latest access_token if it
        has been revoked.
    """
    self.store = store

  def __getstate__(self):
    """Trim the state down to something that can be pickled."""
    d = copy.copy(self.__dict__)
    del d['store']
    return d

  def __setstate__(self, state):
    """Reconstitute the state of the object from being pickled."""
    self.__dict__.update(state)
    self.store = None

  def authorize(self, http):
    """Authorize an httplib2.Http instance with these Credentials

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
      response_code = 302
      http.follow_redirects = False
      while response_code in [301, 302]:
        req = oauth.Request.from_consumer_and_token(
            self.consumer, self.token, http_method=method, http_url=uri)
        req.sign_request(signer, self.consumer, self.token)
        if headers is None:
          headers = {}
        headers.update(req.to_header())
        if 'user-agent' in headers:
          headers['user-agent'] = self.user_agent + ' ' + headers['user-agent']
        else:
          headers['user-agent'] = self.user_agent

        resp, content = request_orig(uri, method, body, headers,
                            redirections, connection_type)
        response_code = resp.status
        if response_code in [301, 302]:
          uri = resp['location']

      # Update the stored credential if it becomes invalid.
      if response_code == 401:
        logging.info('Access token no longer valid: %s' % content)
        self._invalid = True
        if self.store is not None:
          self.store(self)
        raise CredentialsInvalidError("Credentials are no longer valid.")

      return resp, content

    http.request = new_request
    return http


class TwoLeggedOAuthCredentials(Credentials):
  """Two Legged Credentials object for OAuth 1.0a.

  The Two Legged object is created directly, not from a flow.  Once you
  authorize and httplib2.Http instance you can change the requestor and that
  change will propogate to the authorized httplib2.Http instance. For example:

    http = httplib2.Http()
    http = credentials.authorize(http)

    credentials.requestor = 'foo@example.info'
    http.request(...)
    credentials.requestor = 'bar@example.info'
    http.request(...)
  """

  def __init__(self, consumer_key, consumer_secret, user_agent):
    """
    Args:
      consumer_key: string, An OAuth 1.0 consumer key
      consumer_secret: string, An OAuth 1.0 consumer secret
      user_agent: string, The HTTP User-Agent to provide for this application.
    """
    self.consumer = oauth.Consumer(consumer_key, consumer_secret)
    self.user_agent = user_agent
    self.store = None

    # email address of the user to act on the behalf of.
    self._requestor = None

  @property
  def invalid(self):
    """True if the credentials are invalid, such as being revoked.

    Always returns False for Two Legged Credentials.
    """
    return False

  def getrequestor(self):
    return self._requestor

  def setrequestor(self, email):
    self._requestor = email

  requestor = property(getrequestor, setrequestor, None,
      'The email address of the user to act on behalf of')

  def set_store(self, store):
    """Set the storage for the credential.

    Args:
      store: callable, a callable that when passed a Credential
        will store the credential back to where it came from.
        This is needed to store the latest access_token if it
        has been revoked.
    """
    self.store = store

  def __getstate__(self):
    """Trim the state down to something that can be pickled."""
    d = copy.copy(self.__dict__)
    del d['store']
    return d

  def __setstate__(self, state):
    """Reconstitute the state of the object from being pickled."""
    self.__dict__.update(state)
    self.store = None

  def authorize(self, http):
    """Authorize an httplib2.Http instance with these Credentials

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
      response_code = 302
      http.follow_redirects = False
      while response_code in [301, 302]:
        # add in xoauth_requestor_id=self._requestor to the uri
        if self._requestor is None:
          raise MissingParameter(
              'Requestor must be set before using TwoLeggedOAuthCredentials')
        parsed = list(urlparse.urlparse(uri))
        q = parse_qsl(parsed[4])
        q.append(('xoauth_requestor_id', self._requestor))
        parsed[4] = urllib.urlencode(q)
        uri = urlparse.urlunparse(parsed)

        req = oauth.Request.from_consumer_and_token(
            self.consumer, None, http_method=method, http_url=uri)
        req.sign_request(signer, self.consumer, None)
        if headers is None:
          headers = {}
        headers.update(req.to_header())
        if 'user-agent' in headers:
          headers['user-agent'] = self.user_agent + ' ' + headers['user-agent']
        else:
          headers['user-agent'] = self.user_agent
        resp, content = request_orig(uri, method, body, headers,
                            redirections, connection_type)
        response_code = resp.status
        if response_code in [301, 302]:
          uri = resp['location']

      if response_code == 401:
        logging.info('Access token no longer valid: %s' % content)
        # Do not store the invalid state of the Credentials because
        # being 2LO they could be reinstated in the future.
        raise CredentialsInvalidError("Credentials are invalid.")

      return resp, content

    http.request = new_request
    return http


class FlowThreeLegged(Flow):
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
      logging.error('Failed to retrieve temporary authorization: %s', content)
      raise RequestError('Invalid response %s.' % resp['status'])

    self.request_token = dict(parse_qsl(content))

    auth_params = copy.copy(self.params)
    auth_params['oauth_token'] = self.request_token['oauth_token']

    return _oauth_uri('authorize', self.discovery, auth_params)

  def step2_exchange(self, verifier):
    """Exhanges an authorized request token
    for OAuthCredentials.

    Args:
      verifier: string, dict - either the verifier token, or a dictionary
        of the query parameters to the callback, which contains
        the oauth_verifier.
    Returns:
       The Credentials object.
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
      logging.error('Failed to retrieve access token: %s', content)
      raise RequestError('Invalid response %s.' % resp['status'])

    oauth_params = dict(parse_qsl(content))
    token = oauth.Token(
        oauth_params['oauth_token'],
        oauth_params['oauth_token_secret'])

    return OAuthCredentials(consumer, token, self.user_agent)
