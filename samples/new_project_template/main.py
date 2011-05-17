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
"""Starting template for Google App Engine applications.

Use this project as a starting point if you are just beginning to build a Google
App Engine project. Remember to fill in the OAuth 2.0 client_id and
client_secret which can be obtained from the Developer Console
<https://code.google.com/apis/console/>
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'


import httplib2
import logging
import os
import pickle

from apiclient.discovery import build
from oauth2client.appengine import CredentialsProperty
from oauth2client.appengine import StorageByKeyName
from oauth2client.client import OAuth2WebServerFlow
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import login_required

# Set up a Flow object to be used if we need to authenticate. This
# sample uses OAuth 2.0, and we set up the OAuth2WebServerFlow with
# the information it needs to authenticate. Note that it is called
# the Web Server Flow, but it can also handle the flow for native
# applications <http://code.google.com/apis/accounts/docs/OAuth2.html#IA>
# The client_id and client_secret are copied from the Identity tab on
# the Google APIs Console <http://code.google.com/apis/console>

FLOW = OAuth2WebServerFlow(
    client_id='<client id goes here>',
    client_secret='<client secret goes here>',
    scope='https://www.googleapis.com/auth/buzz',
    user_agent='my-sample-app/1.0')


class Credentials(db.Model):
  credentials = CredentialsProperty()


class MainHandler(webapp.RequestHandler):

  @login_required
  def get(self):
    user = users.get_current_user()
    credentials = StorageByKeyName(
        Credentials, user.user_id(), 'credentials').get()

    if not credentials or credentials.invalid:
      return begin_oauth_flow(self, user)

    http = credentials.authorize(httplib2.Http())

    # Build a service object for interacting with the API. Visit
    # the Google APIs Console <http://code.google.com/apis/console>
    # to get a developerKey for your own application.
    service = build("buzz", "v1", http=http)
    followers = service.people().list(
        userId='@me', groupId='@followers').execute()
    text = 'Hello, you have %s followers!' % followers['totalResults']

    path = os.path.join(os.path.dirname(__file__), 'welcome.html')
    self.response.out.write(template.render(path, {'text': text }))


def begin_oauth_flow(request_handler, user):
  callback = request_handler.request.relative_url('/oauth2callback')
  authorize_url = FLOW.step1_get_authorize_url(callback)
  # Here we are using memcache to store the flow temporarily while the user
  # is directed to authorize our service. You could also store the flow
  # in the datastore depending on your utilization of memcache, just remember
  # in that case to clean up the flow after you are done with it.
  memcache.set(user.user_id(), pickle.dumps(FLOW))
  request_handler.redirect(authorize_url)


class OAuthHandler(webapp.RequestHandler):

  @login_required
  def get(self):
    user = users.get_current_user()
    flow = pickle.loads(memcache.get(user.user_id()))
    # This code should be ammended with application specific error
    # handling. The following cases should be considered:
    # 1. What if the flow doesn't exist in memcache? Or is corrupt?
    # 2. What if the step2_exchange fails?
    if flow:
      credentials = flow.step2_exchange(self.request.params)
      StorageByKeyName(
          Credentials, user.user_id(), 'credentials').put(credentials)
      self.redirect("/")
    else:
      # Add application specific error handling here.
      pass


def main():
  application = webapp.WSGIApplication(
      [
      ('/', MainHandler),
      ('/oauth2callback', OAuthHandler)
      ],
      debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
