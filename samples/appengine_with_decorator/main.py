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
from oauth2client.appengine import OAuth2Decorator
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

# The client_id and client_secret are copied from the API Access tab on
# the Google APIs Console <http://code.google.com/apis/console>
decorator = OAuth2Decorator(
    client_id='837647042410-75ifgipj95q4agpm0cs452mg7i2pn17c.apps.googleusercontent.com',
    client_secret='QhxYsjM__u4vy5N0DXUFRwwI',
    scope='https://www.googleapis.com/auth/buzz',
    user_agent='my-sample-app/1.0')

http = httplib2.Http(memcache)
service = build("buzz", "v1", http=http)

class MainHandler(webapp.RequestHandler):

  @decorator.oauth_required
  def get(self):
    http = decorator.http()
    followers = service.people().list(
        userId='@me', groupId='@followers').execute(http)
    self.response.out.write(
        'Hello, you have %s followers!' % followers['totalResults'])

def main():
  application = webapp.WSGIApplication(
      [
       ('/', MainHandler),
      ],
      debug=True)
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
