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

"""An OAuth 2.0 client

Tools for interacting with OAuth 2.0 protected
resources.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import copy
import datetime
import httplib2
import logging
import urllib
import urlparse

try: # pragma: no cover
  import simplejson
except ImportError: # pragma: no cover
  try:
    # Try to import from django, should work on App Engine
    from django.utils import simplejson
  except ImportError:
    # Should work for Python2.6 and higher.
    import json as simplejson

try:
    from urlparse import parse_qsl
except ImportError:
    from cgi import parse_qsl


class Error(Exception):
  """Base error for this module."""
  pass


class FlowExchangeError(Error):
  """Error trying to exchange an authorization grant for an access token."""
  pass


class AccessTokenRefreshError(Error):
  """Error trying to refresh an expired access token."""
  pass


class AccessTokenCredentialsError(Error):
  """Having only the access_token means no refresh is possible."""
  pass


def _abstract():
  raise NotImplementedError('You need to override this function')


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
      oauth2client.client.Credentials
    """
    _abstract()

  def put(self, credentials):
    """Write a credential.

    Args:
      credentials: Credentials, the credentials to store.
    """
    _abstract()


class OAuth2Credentials(Credentials):
  """Credentials object for OAuth 2.0

  Credentials can be applied to an httplib2.Http object using the authorize()
  method, which then signs each request from that object with the OAuth 2.0
  access token.

  OAuth2Credentials objects may be safely pickled and unpickled.
  """

  def __init__(self, access_token, client_id, client_secret, refresh_token,
      token_expiry, token_uri, user_agent):
    """Create an instance of OAuth2Credentials

    This constructor is not usually called by the user, instead
    OAuth2Credentials objects are instantiated by the OAuth2WebServerFlow.

    Args:
      token_uri: string, URI of token endpoint.
      client_id: string, client identifier.
      client_secret: string, client secret.
      access_token: string, access token.
      token_expiry: datetime, when the access_token expires.
      refresh_token: string, refresh token.
      user_agent: string, The HTTP User-Agent to provide for this application.


    Notes:
      store: callable, a callable that when passed a Credential
        will store the credential back to where it came from.
        This is needed to store the latest access_token if it
        has expired and been refreshed.
    """
    self.access_token = access_token
    self.client_id = client_id
    self.client_secret = client_secret
    self.refresh_token = refresh_token
    self.store = None
    self.token_expiry = token_expiry
    self.token_uri = token_uri
    self.user_agent = user_agent

    # True if the credentials have been revoked or expired and can't be
    # refreshed.
    self._invalid = False

  @property
  def invalid(self):
    """True if the credentials are invalid, such as being revoked."""
    return getattr(self, '_invalid', False)

  def set_store(self, store):
    """Set the storage for the credential.

    Args:
      store: callable, a callable that when passed a Credential
        will store the credential back to where it came from.
        This is needed to store the latest access_token if it
        has expired and been refreshed.
    """
    self.store = store

  def __getstate__(self):
    """Trim the state down to something that can be pickled.
    """
    d = copy.copy(self.__dict__)
    del d['store']
    return d

  def __setstate__(self, state):
    """Reconstitute the state of the object from being pickled.
    """
    self.__dict__.update(state)
    self.store = None

  def _generate_refresh_request_body(self):
    """Generate the body that will be used in the refresh request
    """
    body = urllib.urlencode({
      'grant_type': 'refresh_token',
      'client_id': self.client_id,
      'client_secret': self.client_secret,
      'refresh_token': self.refresh_token,
      })
    return body

  def _generate_refresh_request_headers(self):
    """Generate the headers that will be used in the refresh request
    """
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
    }

    if self.user_agent is not None:
      headers['user-agent'] = self.user_agent

    return headers

  def _refresh(self, http_request):
    """Refresh the access_token using the refresh_token.

    Args:
       http: An instance of httplib2.Http.request
           or something that acts like it.
    """
    body = self._generate_refresh_request_body()
    headers = self._generate_refresh_request_headers()

    logging.info("Refresing access_token")
    resp, content = http_request(
        self.token_uri, method='POST', body=body, headers=headers)
    if resp.status == 200:
      # TODO(jcgregorio) Raise an error if loads fails?
      d = simplejson.loads(content)
      self.access_token = d['access_token']
      self.refresh_token = d.get('refresh_token', self.refresh_token)
      if 'expires_in' in d:
        self.token_expiry = datetime.timedelta(
            seconds=int(d['expires_in'])) + datetime.datetime.now()
      else:
        self.token_expiry = None
      if self.store is not None:
        self.store(self)
    else:
      # An {'error':...} response body means the token is expired or revoked,
      # so we flag the credentials as such.
      logging.error('Failed to retrieve access token: %s' % content)
      error_msg = 'Invalid response %s.' % resp['status']
      try:
        d = simplejson.loads(content)
        if 'error' in d:
          error_msg = d['error']
          self._invalid = True
          if self.store is not None:
            self.store(self)
          else:
            logging.warning(
                "Unable to store refreshed credentials, no Storage provided.")
      except:
        pass
      raise AccessTokenRefreshError(error_msg)

  def authorize(self, http):
    """Authorize an httplib2.Http instance with these credentials.

    Args:
       http: An instance of httplib2.Http
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

    # The closure that will replace 'httplib2.Http.request'.
    def new_request(uri, method='GET', body=None, headers=None,
                    redirections=httplib2.DEFAULT_MAX_REDIRECTS,
                    connection_type=None):
      if not self.access_token:
        logging.info("Attempting refresh to obtain initial access_token")
        self._refresh(request_orig)

      """Modify the request headers to add the appropriate
      Authorization header."""
      if headers == None:
        headers = {}
      headers['authorization'] = 'OAuth ' + self.access_token

      if self.user_agent is not None:
        if 'user-agent' in headers:
          headers['user-agent'] = self.user_agent + ' ' + headers['user-agent']
        else:
          headers['user-agent'] = self.user_agent

      resp, content = request_orig(uri, method, body, headers,
                                   redirections, connection_type)

      if resp.status == 401:
        logging.info("Refreshing because we got a 401")
        self._refresh(request_orig)
        headers['authorization'] = 'OAuth ' + self.access_token
        return request_orig(uri, method, body, headers,
                            redirections, connection_type)
      else:
        return (resp, content)

    http.request = new_request
    return http


class AccessTokenCredentials(OAuth2Credentials):
  """Credentials object for OAuth 2.0

  Credentials can be applied to an httplib2.Http object using the authorize()
  method, which then signs each request from that object with the OAuth 2.0
  access token.  This set of credentials is for the use case where you have
  acquired an OAuth 2.0 access_token from another place such as a JavaScript
  client or another web application, and wish to use it from Python. Because
  only the access_token is present it can not be refreshed and will in time
  expire.

  AccessTokenCredentials objects may be safely pickled and unpickled.

  Usage:
    credentials = AccessTokenCredentials('<an access token>',
      'my-user-agent/1.0')
    http = httplib2.Http()
    http = credentials.authorize(http)

  Exceptions:
    AccessTokenCredentialsExpired: raised when the access_token expires or is
      revoked.
  """

  def __init__(self, access_token, user_agent):
    """Create an instance of OAuth2Credentials

    This is one of the few types if Credentials that you should contrust,
    Credentials objects are usually instantiated by a Flow.

    Args:
      access_token: string, access token.
      user_agent: string, The HTTP User-Agent to provide for this application.

    Notes:
      store: callable, a callable that when passed a Credential
        will store the credential back to where it came from.
    """
    super(AccessTokenCredentials, self).__init__(
        access_token,
        None,
        None,
        None,
        None,
        None,
        user_agent)

  def _refresh(self, http_request):
    raise AccessTokenCredentialsError(
        "The access_token is expired or invalid and can't be refreshed.")


class AssertionCredentials(OAuth2Credentials):
  """Abstract Credentials object used for OAuth 2.0 assertion grants

  This credential does not require a flow to instantiate because it represents
  a two legged flow, and therefore has all of the required information to
  generate and refresh its own access tokens.  It must be subclassed to
  generate the appropriate assertion string.

  AssertionCredentials objects may be safely pickled and unpickled.
  """

  def __init__(self, assertion_type, user_agent,
      token_uri='https://accounts.google.com/o/oauth2/token', **kwargs):
    """Constructor for AssertionFlowCredentials

    Args:
      assertion_type: string, assertion type that will be declared to the auth
          server
      user_agent: string, The HTTP User-Agent to provide for this application.
      token_uri: string, URI for token endpoint. For convenience
        defaults to Google's endpoints but any OAuth 2.0 provider can be used.
    """
    super(AssertionCredentials, self).__init__(
        None,
        None,
        None,
        None,
        None,
        token_uri,
        user_agent)
    self.assertion_type = assertion_type

  def _generate_refresh_request_body(self):
    assertion = self._generate_assertion()

    body = urllib.urlencode({
      'assertion_type': self.assertion_type,
      'assertion': assertion,
      'grant_type': "assertion",
    })

    return body

  def _generate_assertion(self):
    """Generate the assertion string that will be used in the access token
    request.
    """
    _abstract()


class OAuth2WebServerFlow(Flow):
  """Does the Web Server Flow for OAuth 2.0.

  OAuth2Credentials objects may be safely pickled and unpickled.
  """

  def __init__(self, client_id, client_secret, scope, user_agent,
      auth_uri='https://accounts.google.com/o/oauth2/auth',
      token_uri='https://accounts.google.com/o/oauth2/token',
      **kwargs):
    """Constructor for OAuth2WebServerFlow

    Args:
      client_id: string, client identifier.
      client_secret: string client secret.
      scope: string, scope of the credentials being requested.
      user_agent: string, HTTP User-Agent to provide for this application.
      auth_uri: string, URI for authorization endpoint. For convenience
        defaults to Google's endpoints but any OAuth 2.0 provider can be used.
      token_uri: string, URI for token endpoint. For convenience
        defaults to Google's endpoints but any OAuth 2.0 provider can be used.
      **kwargs: dict, The keyword arguments are all optional and required
                        parameters for the OAuth calls.
    """
    self.client_id = client_id
    self.client_secret = client_secret
    self.scope = scope
    self.user_agent = user_agent
    self.auth_uri = auth_uri
    self.token_uri = token_uri
    self.params = kwargs
    self.redirect_uri = None

  def step1_get_authorize_url(self, redirect_uri='oob'):
    """Returns a URI to redirect to the provider.

    Args:
      redirect_uri: string, Either the string 'oob' for a non-web-based
                    application, or a URI that handles the callback from
                    the authorization server.

    If redirect_uri is 'oob' then pass in the
    generated verification code to step2_exchange,
    otherwise pass in the query parameters received
    at the callback uri to step2_exchange.
    """

    self.redirect_uri = redirect_uri
    query = {
      'response_type': 'code',
      'client_id': self.client_id,
      'redirect_uri': redirect_uri,
      'scope': self.scope,
      }
    query.update(self.params)
    parts = list(urlparse.urlparse(self.auth_uri))
    query.update(dict(parse_qsl(parts[4]))) # 4 is the index of the query part
    parts[4] = urllib.urlencode(query)
    return urlparse.urlunparse(parts)

  def step2_exchange(self, code, http=None):
    """Exhanges a code for OAuth2Credentials.

    Args:
      code: string or dict, either the code as a string, or a dictionary
        of the query parameters to the redirect_uri, which contains
        the code.
      http: httplib2.Http, optional http instance to use to do the fetch
    """

    if not (isinstance(code, str) or isinstance(code, unicode)):
      code = code['code']

    body = urllib.urlencode({
      'grant_type': 'authorization_code',
      'client_id': self.client_id,
      'client_secret': self.client_secret,
      'code': code,
      'redirect_uri': self.redirect_uri,
      'scope': self.scope,
      })
    headers = {
      'content-type': 'application/x-www-form-urlencoded',
    }

    if self.user_agent is not None:
      headers['user-agent'] = self.user_agent

    if http is None:
      http = httplib2.Http()
    resp, content = http.request(self.token_uri, method='POST', body=body,
                                 headers=headers)
    if resp.status == 200:
      # TODO(jcgregorio) Raise an error if simplejson.loads fails?
      d = simplejson.loads(content)
      access_token = d['access_token']
      refresh_token = d.get('refresh_token', None)
      token_expiry = None
      if 'expires_in' in d:
        token_expiry = datetime.datetime.now() + datetime.timedelta(
            seconds=int(d['expires_in']))

      logging.info('Successfully retrieved access token: %s' % content)
      return OAuth2Credentials(access_token, self.client_id,
                               self.client_secret, refresh_token, token_expiry,
                               self.token_uri, self.user_agent)
    else:
      logging.error('Failed to retrieve access token: %s' % content)
      error_msg = 'Invalid response %s.' % resp['status']
      try:
        d = simplejson.loads(content)
        if 'error' in d:
          error_msg = d['error']
      except:
        pass

      raise FlowExchangeError(error_msg)
