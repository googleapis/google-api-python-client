#!/usr/bin/env python
#
# Copyright 2011 Google Inc.
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
import os
import pydoc
import re

from apiclient.anyjson import simplejson
from apiclient import discovery
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util


class MainHandler(webapp.RequestHandler):
  """Handles serving the main landing page.
  """

  def get(self):
    http = httplib2.Http(memcache)
    resp, content = http.request('https://www.googleapis.com/discovery/v1/apis?preferred=true')
    directory = simplejson.loads(content)['items']
    for item in directory:
      item['title'] = item.get('title', item.get('description', ''))
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(
        template.render(
            path, {'directory': directory,
                   }))


class GadgetHandler(webapp.RequestHandler):
  """Handles serving the Google Gadget.
  """

  def get(self):
    http = httplib2.Http(memcache)
    resp, content = http.request('https://www.googleapis.com/discovery/v1/apis?preferred=true')
    directory = simplejson.loads(content)['items']
    for item in directory:
      item['title'] = item.get('title', item.get('description', ''))
    path = os.path.join(os.path.dirname(__file__), 'gadget.html')
    self.response.out.write(
        template.render(
            path, {'directory': directory,
                   }))
    self.response.headers.add_header('Content-Type', 'application/xml')


def _render(resource):
  """Use pydoc helpers on an instance to generate the help documentation.
  """
  obj, name = pydoc.resolve(type(resource))
  return pydoc.html.page(
      pydoc.describe(obj), pydoc.html.document(obj, name))


class ResourceHandler(webapp.RequestHandler):
  """Handles serving the PyDoc for a given collection.
  """

  def get(self, service_name, version, collection):
    resource = discovery.build(service_name, version)
    # descend the object path
    if collection:
      path = collection.split('/')
      if path:
        for method in path:
          resource = getattr(resource, method)()
    page = _render(resource)

    collections = []
    for name in dir(resource):
      if not "_" in name and callable(getattr(resource, name)) and hasattr(
          getattr(resource, name), '__is_resource__'):
        collections.append(name)

    if collection is None:
      collection_path = ''
    else:
      collection_path = collection + '/'
    for name in collections:
      page = re.sub('strong>(%s)<' % name,
          r'strong><a href="/%s/%s/%s">\1</a><' % (
          service_name, version, collection_path + name), page)

    # TODO(jcgregorio) breadcrumbs
    # TODO(jcgregorio) sample code?
    page = re.sub('<p>', r'<a href="/">Home</a><p>', page, 1)
    self.response.out.write(page)


def main():
  application = webapp.WSGIApplication(
      [
      (r'/', MainHandler),
      (r'/_gadget/', GadgetHandler),
      (r'/([^\/]*)/([^\/]*)(?:/(.*))?', ResourceHandler),
      ],
      debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
