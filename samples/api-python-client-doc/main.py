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


import inspect
import pydoc
import re

from apiclient.discovery import build

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util


class MainHandler(webapp.RequestHandler):

  def get(self):
    self.response.out.write("""
    <h1>Google API Client for Python Documentation</h1>
    <ul>
      <li><a href='/buzz/v1'>buzz</a>
      <li><a href='/moderator/v1'>moderator</a>
      <li><a href='/latitude/v1'>latitude</a>
      <li><a href='/customsearch/v1'>customsearch</a>
      <li><a href='/diacritize/v1'>diacritize</a>
      <li><a href='/translate/v2'>translate</a>
      <li><a href='/prediction/v1.1'>prediction</a>
      <li><a href='/shopping/v1'>shopping</a>
      <li><a href='/urlshortener/v1'>urlshortener</a>
    </ul>
    """)


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
