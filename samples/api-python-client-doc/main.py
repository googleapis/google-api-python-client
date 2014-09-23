#!/usr/bin/env python
#
# Copyright 2014 Google Inc. All Rights Reserved.
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
"""Sample application for Python documentation of APIs.

This is running live at http://api-python-client-doc.appspot.com where it
provides a list of APIs and PyDoc documentation for all the generated API
surfaces as they appear in the google-api-python-client. In addition it also
provides a Google Gadget.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import httplib2
import inspect
import json
import logging
import os
import pydoc
import re

import describe
import uritemplate

from googleapiclient import discovery
from googleapiclient.errors import HttpError
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util


DISCOVERY_URI = 'https://www.googleapis.com/discovery/v1/apis?preferred=true'


def get_directory_doc():
  http = httplib2.Http(memcache)
  ip = os.environ.get('REMOTE_ADDR', None)
  uri = DISCOVERY_URI
  if ip:
    uri += ('&userIp=' + ip)
  resp, content = http.request(uri)
  directory = json.loads(content)['items']
  for item in directory:
    item['title'] = item.get('title', item.get('description', ''))
    item['safe_version'] = describe.safe_version(item['version'])
  return directory


class MainHandler(webapp.RequestHandler):
  """Handles serving the main landing page.
  """

  def get(self):
    directory = get_directory_doc()
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(
        template.render(
            path, {'directory': directory,
                   }))


class GadgetHandler(webapp.RequestHandler):
  """Handles serving the Google Gadget."""

  def get(self):
    directory = get_directory_doc()
    path = os.path.join(os.path.dirname(__file__), 'gadget.html')
    self.response.out.write(
        template.render(
            path, {'directory': directory,
                   }))
    self.response.headers.add_header('Content-Type', 'application/xml')


class EmbedHandler(webapp.RequestHandler):
  """Handles serving a front page suitable for embedding."""

  def get(self):
    directory = get_directory_doc()
    path = os.path.join(os.path.dirname(__file__), 'embed.html')
    self.response.out.write(
        template.render(
            path, {'directory': directory,
                   }))


class ResourceHandler(webapp.RequestHandler):
  """Handles serving the PyDoc for a given collection.
  """

  def get(self, service_name, version, collection):

    return self.redirect('https://google-api-client-libraries.appspot.com/documentation/%s/%s/python/latest/%s_%s.%s.html'
        % (service_name, version, service_name, version, collection))


def main():
  application = webapp.WSGIApplication(
      [
      (r'/', MainHandler),
      (r'/_gadget/', GadgetHandler),
      (r'/_embed/', EmbedHandler),
      (r'/([^_]+)_([^\.]+)(?:\.(.*))?\.html$', ResourceHandler),
      ],
      debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
