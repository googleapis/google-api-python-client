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

import httplib2
import oauth2 as oauth
import simplejson


def oauth_wrap(consumer, token, http):
    """
    Args:
       http - An instance of httplib2.Http
           or something that acts like it.

    Returns:
       A modified instance of http that was passed in.

    Example:

      h = httplib2.Http()
      h = oauth_wrap(h)

    Grumble. You can't create a new OAuth
    subclass of httplib2.Authenication because
    it never gets passed the absolute URI, which is
    needed for signing. So instead we have to overload
    'request' with a closure that adds in the
    Authorization header and then calls the original version
    of 'request().
    """
    request_orig = http.request
    signer = oauth.SignatureMethod_HMAC_SHA1()

    def new_request(uri, method='GET', body=None, headers=None,
        redirections=httplib2.DEFAULT_MAX_REDIRECTS, connection_type=None):
      """Modify the request headers to add the appropriate
      Authorization header."""
      req = oauth.Request.from_consumer_and_token(
          consumer, token, http_method=method, http_url=uri)
      req.sign_request(signer, consumer, token)
      if headers == None:
        headers = {}
      headers.update(req.to_header())
      headers['user-agent'] = 'jcgregorio-test-client'
      return request_orig(uri, method, body, headers, redirections,
          connection_type)

    http.request = new_request
    return http

def get_authorised_http(oauth_params):
  consumer = oauth.Consumer(oauth_params['consumer_key'],
      oauth_params['consumer_secret'])
  token = oauth.Token(oauth_params['oauth_token'],
      oauth_params['oauth_token_secret'])

  # Create a simple monkeypatch for httplib2.Http.request
  # just adds in the oauth authorization header and then calls
  # the original request().
  http = httplib2.Http()
  return oauth_wrap(consumer, token, http)

def get_wrapped_http(filename='oauth_token.dat'):
  f = open(filename, 'r')
  oauth_params = simplejson.loads(f.read())

  return get_authorised_http(oauth_params)
