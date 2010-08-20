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

__author__ = 'ade@google.com'

import apiclient.discovery
import logging
import oauth_wrap
import oauth2 as oauth
import urllib
import urlparse

try:
  from urlparse import parse_qs, parse_qsl, urlparse
except ImportError:
  from cgi import parse_qs, parse_qsl

# TODO(ade) Replace user-agent with something specific
HEADERS = {
  'user-agent': 'gdata-python-v3-sample-client/0.1',
  'content-type': 'application/x-www-form-urlencoded'
  }

REQUEST_TOKEN_URL = 'https://www.google.com/accounts/OAuthGetRequestToken?domain=anonymous&scope=https://www.googleapis.com/auth/buzz'
AUTHORIZE_URL = 'https://www.google.com/buzz/api/auth/OAuthAuthorizeToken?domain=anonymous&scope=https://www.googleapis.com/auth/buzz'
ACCESS_TOKEN_URL = 'https://www.google.com/accounts/OAuthGetAccessToken'

class BuzzGaeClient(object):
  def __init__(self, consumer_key='anonymous', consumer_secret='anonymous'):
    self.consumer = oauth.Consumer(consumer_key, consumer_secret)
    self.consumer_key = consumer_key
    self.consumer_secret = consumer_secret

  def _make_post_request(self, client, url, parameters):
    resp, content = client.request(url, 'POST', headers=HEADERS,
        body=urllib.urlencode(parameters, True))

    if resp['status'] != '200':
      logging.warn('Request: %s failed with status: %s. Content was: %s' % (url, resp['status'], content))
      raise Exception('Invalid response %s.' % resp['status'])
    return resp, content

  def get_request_token(self, callback_url, display_name = None):
    parameters = {
      'oauth_callback': callback_url
      }

    if display_name is not None:
      parameters['xoauth_displayname'] = display_name

    client = oauth.Client(self.consumer)
    resp, content = self._make_post_request(client, REQUEST_TOKEN_URL, parameters)

    request_token = dict(parse_qsl(content))
    return request_token

  def generate_authorisation_url(self, request_token):
    """Returns the URL the user should be redirected to in other to gain access to their account."""
    
    base_url = urlparse.urlparse(AUTHORIZE_URL)
    query = parse_qs(base_url.query)
    query['oauth_token'] = request_token['oauth_token']

    logging.info(urllib.urlencode(query, True))

    url = (base_url.scheme, base_url.netloc, base_url.path, base_url.params,
      urllib.urlencode(query, True), base_url.fragment)
    authorisation_url = urlparse.urlunparse(url)
    return authorisation_url

  def upgrade_to_access_token(self, request_token, oauth_verifier):
    token = oauth.Token(request_token['oauth_token'],
    request_token['oauth_token_secret'])
    token.set_verifier(oauth_verifier)
    client = oauth.Client(self.consumer, token)

    parameters = {}
    resp, content = self._make_post_request(client, ACCESS_TOKEN_URL, parameters)
    access_token = dict(parse_qsl(content))

    d = {
      'consumer_key' : self.consumer_key,
      'consumer_secret' : self.consumer_secret
      }
    d.update(access_token)
    return d

  def build_api_client(self, oauth_params=None):
    if oauth_params is not None:
      http = oauth_wrap.get_authorised_http(oauth_params)
      return apiclient.discovery.build('buzz', 'v1', http = http)
    else:
      return apiclient.discovery.build('buzz', 'v1')
