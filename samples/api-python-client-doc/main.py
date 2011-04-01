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
import inspect
import os
import pydoc
import re

from apiclient.discovery import build
from apiclient.anyjson import simplejson
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util


class MainHandler(webapp.RequestHandler):

  def get(self):
    http = httplib2.Http(memcache)
    resp, content = http.request('https://www.googleapis.com/discovery/v0.3/directory?preferred=true')
    directory = simplejson.loads(content)['items']
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(
        template.render(
            path, {'directory': directory,
                   }))


def render(resource):
  obj, name = pydoc.resolve(type(resource))
  return pydoc.html.page(
      pydoc.describe(obj), pydoc.html.document(obj, name))


class ResourceHandler(webapp.RequestHandler):

  def get(self, service_name, version, collection):
    resource = build(service_name, version)
    # descend the object path
    if collection:
      path = collection.split('/')
      if path:
        for method in path:
          resource = getattr(resource, method)()
    page = render(resource)

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
      (r'/([^\/]*)/([^\/]*)(?:/(.*))?', ResourceHandler),
      ],
      debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
