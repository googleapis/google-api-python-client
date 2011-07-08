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

Use this project as a starting point if you are just beginning to build a
Google App Engine project which will access and manage data held under a role
account for the App Engine app.  More information about using Google App Engine
apps to call Google APIs can be found in Scenario 1 of the following document:

<https://sites.google.com/site/oauthgoog/Home/google-oauth2-assertion-flow>
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'


import httplib2
import logging
import os
import pickle

from apiclient.discovery import build
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from oauth2client.appengine import AppAssertionCredentials

credentials = AppAssertionCredentials(
    scope='https://www.googleapis.com/auth/urlshortener')

http = credentials.authorize(httplib2.Http(memcache))
service = build("urlshortener", "v1", http=http)


class MainHandler(webapp.RequestHandler):

  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'welcome.html')
    shortened = service.url().list().execute()
    short_and_long = [(item["id"], item["longUrl"]) for item in
        shortened["items"]]

    variables = {
        'short_and_long': short_and_long,
        }
    self.response.out.write(template.render(path, variables))

  def post(self):
    long_url = self.request.get("longUrl")
    shortened = service.url().insert(body={"longUrl": long_url}).execute()
    self.redirect("/")


def main():
  application = webapp.WSGIApplication(
      [
       ('/', MainHandler),
      ],
      debug=True)
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
