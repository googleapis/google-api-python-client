#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""One-line documentation for discovery module.

A detailed description of discovery.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'


from apiclient.discovery import build

import httplib2
import oauth2 as oauth
import re
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
    of 'request()'.
    """
    request_orig = http.request
    signer = oauth.SignatureMethod_HMAC_SHA1()

    def new_request(uri, method="GET", body=None, headers=None,
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
      return request_orig(uri, method, body, headers,
          redirections, connection_type)

    http.request = new_request
    return http


def get_wrapped_http():
  f = open("oauth_token.dat", "r")
  oauth_params = simplejson.loads(f.read())

  consumer = oauth.Consumer(
      oauth_params['consumer_key'], oauth_params['consumer_secret'])
  token = oauth.Token(
      oauth_params['oauth_token'], oauth_params['oauth_token_secret'])

  # Create a simple monkeypatch for httplib2.Http.request
  # just adds in the oauth authorization header and then calls
  # the original request().
  http = httplib2.Http()
  return oauth_wrap(consumer, token, http)


def main():
  http = get_wrapped_http()
  p = build("buzz", "v1", http=http)
  activities = p.activities()
  activitylist = activities.list(scope='@self', userId='@me')
  print activitylist['items'][0]['title']
  activities.insert(userId='@me', body={
    'title': 'Testing insert',
    'object': {
      'content': u'Just a short note to show that insert is working. ☄',
      'type': 'note'}
    }
  )

if __name__ == '__main__':
  main()
