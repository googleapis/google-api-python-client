#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

__author__ = 'jcgregorio@google.com (Joe Gregorio)'


import httplib2
import logging
import os
import pickle

from apiclient.discovery import build
from apiclient.ext.appengine import FlowThreeLeggedProperty
from apiclient.ext.appengine import OAuthCredentialsProperty
from apiclient.ext.appengine import StorageByKeyName
from apiclient.oauth import FlowThreeLegged
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import login_required

APP_ID = os.environ['APPLICATION_ID']

if 'Development' in os.environ['SERVER_SOFTWARE']:
  STEP2_URI = 'http://localhost:8080/auth_return'
else:
  STEP2_URI = 'http://%s.appspot.com/auth_return' % APP_ID


class Credentials(db.Model):
  credentials = OAuthCredentialsProperty()


class MainHandler(webapp.RequestHandler):

  @login_required
  def get(self):
    user = users.get_current_user()
    storage = StorageByKeyName(Credentials, user.user_id(), 'credentials')
    http = httplib2.Http()
    credentials = storage.get()

    if credentials:
      http = credentials.authorize(http)

    service = build("buzz", "v1", http=http)

    if not credentials:
      return begin_oauth_flow(self, user, service)

    followers = service.people().list(
        userId='@me', groupId='@followers').execute()
    self.response.out.write('Hello, you have %s followers!' %
                            followers['totalResults'])


def begin_oauth_flow(request_handler, user, service):
    flow = FlowThreeLegged(service.auth_discovery(),
                   consumer_key='anonymous',
                   consumer_secret='anonymous',
                   user_agent='%s/1.0' % APP_ID,
                   domain='anonymous',
                   scope='https://www.googleapis.com/auth/buzz',
                   xoauth_displayname='App Name')

    authorize_url = flow.step1_get_authorize_url(STEP2_URI)
    memcache.set(user.user_id(), pickle.dumps(flow))
    request_handler.redirect(authorize_url)


class OAuthHandler(webapp.RequestHandler):

  @login_required
  def get(self):
    user = users.get_current_user()
    storage = StorageByKeyName(Credentials, user.user_id(), 'credentials')
    flow = pickle.loads(memcache.get(user.user_id()))
    credentials = flow.step2_exchange(self.request.params)
    storage.put(credentials)
    self.redirect("/")


def main():
  application = webapp.WSGIApplication(
      [
      ('/', MainHandler),
      ('/auth_return', OAuthHandler)
      ],
      debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
