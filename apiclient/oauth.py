#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Utilities for OAuth.

Utilities for making it easier to work with OAuth.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import copy
import urllib
import oauth2 as oauth

try:
    from urlparse import parse_qs, parse_qsl
except ImportError:
    from cgi import parse_qs, parse_qsl
class MissingParameter(Exception):
  pass

def abstract():
  raise NotImplementedError("You need to override this function")


class TokenStore(object):
  def get(user, service):
    """Returns an oauth.Token based on the (user, service) returning
    None if there is no Token for that (user, service).
    """
    abstract()

  def set(user, service, token):
    abstract()

buzz_discovery = {
    'required': ['domain', 'scope'],
    'request': {
        'url': 'https://www.google.com/accounts/OAuthGetRequestToken',
        'params': ['xoauth_displayname']
        },
    'authorize': {
        'url': 'https://www.google.com/buzz/api/auth/OAuthAuthorizeToken',
        'params': ['iconUrl', 'oauth_token']
        },
    'access': {
        'url': 'https://www.google.com/accounts/OAuthGetAccessToken',
        'params': []
        },
    }

def _oauth_uri(name, discovery, params):
  if name not in ['request', 'access', 'authorize']:
    raise KeyError(name)
  keys = []
  keys.extend(discovery['required'])
  keys.extend(discovery[name]['params'])
  query = {}
  for key in keys:
    if key in params:
      query[key] = params[key]
  return discovery[name]['url'] + '?' + urllib.urlencode(query)

class Flow3LO(object):
  def __init__(self, discovery, consumer_key, consumer_secret, user_agent,
               **kwargs):
    self.discovery = discovery
    self.consumer_key = consumer_key
    self.consumer_secret = consumer_secret
    self.user_agent = user_agent
    self.params = kwargs
    self.request_token = {}
    for key in discovery['required']:
      if key not in self.params:
        raise MissingParameter('Required parameter %s not supplied' % key)

  def step1(self, oauth_callback='oob'):
    """Returns a URI to redirect to the provider.

    If oauth_callback is 'oob' then the next call
    should be to step2_pin, otherwise oauth_callback
    is a URI and the next call should be to
    step2_callback() with the query parameters
    received at that callback.
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
      print content
      raise Exception('Invalid response %s.' % resp['status'])

    self.request_token = dict(parse_qsl(content))

    auth_params = copy.copy(self.params)
    auth_params['oauth_token'] = self.request_token['oauth_token']

    uri = _oauth_uri('authorize', self.discovery, auth_params)
    return uri

  def step2_pin(self, pin):
    """Returns an oauth_token and oauth_token_secret in a dictionary"""

    token = oauth.Token(self.request_token['oauth_token'],
        self.request_token['oauth_token_secret'])
    token.set_verifier(pin)
    consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
    client = oauth.Client(consumer, token)

    headers = {
        'user-agent': self.user_agent,
        'content-type': 'application/x-www-form-urlencoded'
    }

    uri = _oauth_uri('access', self.discovery, self.params)
    resp, content = client.request(uri, 'POST', headers=headers)
    return dict(parse_qsl(content))

  def step2_callback(self, query_params):
    """Returns an access token via oauth.Token"""
    pass
