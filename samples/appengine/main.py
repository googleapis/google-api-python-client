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


FLOW = OAuth2WebServerFlow(
    # Visit https://code.google.com/apis/console to
    # generate your client_id, client_secret and to
    # register your redirect_uri.
    client_id='<YOUR CLIENT ID HERE>',
    client_secret='<YOUR CLIENT SECRET HERE>',
    scope='https://www.googleapis.com/auth/buzz',
    user_agent='buzz-cmdline-sample/1.0')


class Credentials(db.Model):
  credentials = CredentialsProperty()


class MainHandler(webapp.RequestHandler):

  @login_required
  def get(self):
    user = users.get_current_user()
    credentials = StorageByKeyName(
        Credentials, user.user_id(), 'credentials').get()

    if credentials is None or credentials.invalid == True:
      callback = self.request.relative_url('/oauth2callback')
      authorize_url = FLOW.step1_get_authorize_url(callback)
      memcache.set(user.user_id(), pickle.dumps(FLOW))
      self.redirect(authorize_url)
    else:
      http = httplib2.Http()
      http = credentials.authorize(http)
      service = build("buzz", "v1", http=http)
      activities = service.activities()
      activitylist = activities.list(scope='@consumption',
                                     userId='@me').execute()
      path = os.path.join(os.path.dirname(__file__), 'welcome.html')
      logout = users.create_logout_url('/')
      self.response.out.write(
          template.render(
              path, {'activitylist': activitylist,
                     'logout': logout
                     }))


class OAuthHandler(webapp.RequestHandler):

  @login_required
  def get(self):
    user = users.get_current_user()
    flow = pickle.loads(memcache.get(user.user_id()))
    if flow:
      credentials = flow.step2_exchange(self.request.params)
      StorageByKeyName(
          Credentials, user.user_id(), 'credentials').put(credentials)
      self.redirect("/")
    else:
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
