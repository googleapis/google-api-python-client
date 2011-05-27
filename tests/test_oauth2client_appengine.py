#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc.
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


"""Discovery document tests

Unit tests for objects created from discovery documents.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import httplib2
import unittest
import urlparse

try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

from apiclient.http import HttpMockSequence
from apiclient.anyjson import simplejson
from webtest import TestApp
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import FlowExchangeError
from oauth2client.appengine import OAuth2Decorator
from google.appengine.ext import webapp
from google.appengine.api import users
from oauth2client.appengine import OAuth2Handler
from google.appengine.ext import testbed


class UserMock(object):
  """Mock the app engine user service"""
  def user_id(self):
    return 'foo_user'


class Http2Mock(object):
  """Mock httplib2.Http"""
  status = 200
  content = {
      'access_token': 'foo_access_token',
      'refresh_token': 'foo_refresh_token',
      'expires_in': 3600
    }

  def request(self, token_uri, method, body, headers, *args, **kwargs):
    self.body = body
    self.headers = headers
    return (self, simplejson.dumps(self.content))


class DecoratorTests(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()
    self.testbed.init_user_stub()

    decorator = OAuth2Decorator(client_id='foo_client_id',
                                client_secret='foo_client_secret',
                                scope='foo_scope',
                                user_agent='foo_user_agent')
    self.decorator = decorator


    class TestRequiredHandler(webapp.RequestHandler):
      @decorator.oauth_required
      def get(self):
        pass


    class TestAwareHandler(webapp.RequestHandler):
      @decorator.oauth_aware
      def get(self):
        self.response.out.write('Hello World!')


    application = webapp.WSGIApplication([('/oauth2callback', OAuth2Handler),
                                          ('/foo_path', TestRequiredHandler),
                                          ('/bar_path', TestAwareHandler)],
                                         debug=True)
    self.app = TestApp(application)
    users.get_current_user = UserMock
    self.httplib2_orig = httplib2.Http
    httplib2.Http = Http2Mock

  def tearDown(self):
    self.testbed.deactivate()
    httplib2.Http = self.httplib2_orig

  def test_required(self):
    # An initial request to an oauth_required decorated path should be a
    # redirect to start the OAuth dance.
    response = self.app.get('/foo_path')
    self.assertTrue(response.status.startswith('302'))
    q = parse_qs(response.headers['Location'].split('?', 1)[1])
    self.assertEqual('http://localhost/oauth2callback', q['redirect_uri'][0])
    self.assertEqual('foo_client_id', q['client_id'][0])
    self.assertEqual('foo_scope', q['scope'][0])
    self.assertEqual('http://localhost/foo_path', q['state'][0])
    self.assertEqual('code', q['response_type'][0])
    self.assertEqual(False, self.decorator.has_credentials())

    # Now simulate the callback to /oauth2callback
    response = self.app.get('/oauth2callback', {
        'code': 'foo_access_code',
        'state': 'foo_path'
        })
    self.assertEqual('http://localhost/foo_path', response.headers['Location'])
    self.assertEqual(None, self.decorator.credentials)

    # Now requesting the decorated path should work
    response = self.app.get('/foo_path')
    self.assertEqual('200 OK', response.status)
    self.assertEqual(True, self.decorator.has_credentials())
    self.assertEqual('foo_refresh_token', self.decorator.credentials.refresh_token)
    self.assertEqual('foo_access_token', self.decorator.credentials.access_token)

    # Invalidate the stored Credentials
    self.decorator.credentials._invalid = True
    self.decorator.credentials.store(self.decorator.credentials)

    # Invalid Credentials should start the OAuth dance again
    response = self.app.get('/foo_path')
    self.assertTrue(response.status.startswith('302'))
    q = parse_qs(response.headers['Location'].split('?', 1)[1])
    self.assertEqual('http://localhost/oauth2callback', q['redirect_uri'][0])

  def test_aware(self):
    # An initial request to an oauth_aware decorated path should not redirect
    response = self.app.get('/bar_path')
    self.assertEqual('Hello World!', response.body)
    self.assertEqual('200 OK', response.status)
    self.assertEqual(False, self.decorator.has_credentials())
    url = self.decorator.authorize_url()
    q = parse_qs(url.split('?', 1)[1])
    self.assertEqual('http://localhost/oauth2callback', q['redirect_uri'][0])
    self.assertEqual('foo_client_id', q['client_id'][0])
    self.assertEqual('foo_scope', q['scope'][0])
    self.assertEqual('http://localhost/bar_path', q['state'][0])
    self.assertEqual('code', q['response_type'][0])

    # Now simulate the callback to /oauth2callback
    url = self.decorator.authorize_url()
    response = self.app.get('/oauth2callback', {
        'code': 'foo_access_code',
        'state': 'bar_path'
        })
    self.assertEqual('http://localhost/bar_path', response.headers['Location'])
    self.assertEqual(False, self.decorator.has_credentials())

    # Now requesting the decorated path will have credentials
    response = self.app.get('/bar_path')
    self.assertEqual('200 OK', response.status)
    self.assertEqual('Hello World!', response.body)
    self.assertEqual(True, self.decorator.has_credentials())
    self.assertEqual('foo_refresh_token', self.decorator.credentials.refresh_token)
    self.assertEqual('foo_access_token', self.decorator.credentials.access_token)

if __name__ == '__main__':
  unittest.main()
