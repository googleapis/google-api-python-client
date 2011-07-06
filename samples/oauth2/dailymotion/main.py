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
    client_id='2ad565600216d25d9cde',
    client_secret='03b56df2949a520be6049ff98b89813f17b467dc',
    scope='read',
    user_agent='oauth2client-sample/1.0',
    auth_uri='https://api.dailymotion.com/oauth/authorize',
    token_uri='https://api.dailymotion.com/oauth/token'
    )


class Credentials(db.Model):
  credentials = CredentialsProperty()


class MainHandler(webapp.RequestHandler):

  @login_required
  def get(self):
    user = users.get_current_user()
    credentials = StorageByKeyName(
        Credentials, user.user_id(), 'credentials').get()

    if credentials is None or credentials.invalid == True:
      callback = self.request.relative_url('/auth_return')
      authorize_url = FLOW.step1_get_authorize_url(callback)
      memcache.set(user.user_id(), pickle.dumps(FLOW))
      self.redirect(authorize_url)
    else:
      http = httplib2.Http()
      http = credentials.authorize(http)

      resp, content = http.request('https://api.dailymotion.com/me')

      path = os.path.join(os.path.dirname(__file__), 'welcome.html')
      logout = users.create_logout_url('/')
      variables = {
          'content': content,
          'logout': logout
          }
      self.response.out.write(template.render(path, variables))


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
      ('/auth_return', OAuthHandler)
      ],
      debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
