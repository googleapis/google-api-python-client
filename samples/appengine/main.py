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

from apiclient.discovery import build
from apiclient.ext.appengine import FlowThreeLeggedProperty
from apiclient.ext.appengine import OAuthCredentialsProperty
from apiclient.oauth import FlowThreeLegged
from apiclient.oauth import buzz_discovery
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import login_required

STEP2_URI = 'http://%s.appspot.com/auth_return' % os.environ['APPLICATION_ID']


class Flow(db.Model):
  # FlowThreeLegged could also be stored in memcache.
  flow = FlowThreeLeggedProperty()


class Credentials(db.Model):
  credentials = OAuthCredentialsProperty()


class MainHandler(webapp.RequestHandler):

  @login_required
  def get(self):
    user = users.get_current_user()
    c = Credentials.get_by_key_name(user.user_id())

    if c:
      http = httplib2.Http()
      http = c.credentials.authorize(http)
      p = build("buzz", "v1", http=http)
      activities = p.activities()
      activitylist = activities.list(scope='@consumption',
                                     userId='@me').execute()
      logging.info(activitylist)
      path = os.path.join(os.path.dirname(__file__), 'welcome.html')
      logout = users.create_logout_url('/')
      self.response.out.write(
          template.render(
              path, {'activitylist': activitylist,
                     'logout': logout
                     }))
    else:
      flow = FlowThreeLegged(buzz_discovery,
                     consumer_key='anonymous',
                     consumer_secret='anonymous',
                     user_agent='google-api-client-python-buzz-webapp/1.0',
                     domain='anonymous',
                     scope='https://www.googleapis.com/auth/buzz',
                     xoauth_displayname='Example Web App')

      authorize_url = flow.step1_get_authorize_url(STEP2_URI)
      f = Flow(key_name=user.user_id(), flow=flow)
      f.put()
      self.redirect(authorize_url)


class OAuthHandler(webapp.RequestHandler):

  @login_required
  def get(self):
    user = users.get_current_user()
    f = Flow.get_by_key_name(user.user_id())
    if f:
      credentials = f.flow.step2_exchange(self.request.params)
      c = Credentials(key_name=user.user_id(), credentials=credentials)
      c.put()
      f.delete()
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
