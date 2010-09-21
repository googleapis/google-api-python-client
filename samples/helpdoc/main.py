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
import logging
import os
import pydoc
import re

from apiclient.discovery import build

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

STEP2_URI = 'http://%s.appspot.com/auth_return' % os.environ['APPLICATION_ID']


# Replicate render_doc here from pydoc.py as it isn't available in Python 2.5
class _OldStyleClass: pass

def render_doc(thing, title='Python Library Documentation: %s', forceload=0):
    """Render text documentation, given an object or a path to an object."""
    object, name = pydoc.resolve(thing, forceload)
    desc = pydoc.describe(object)
    module = inspect.getmodule(object)
    if name and '.' in name:
        desc += ' in ' + name[:name.rfind('.')]
    elif module and module is not object:
        desc += ' in module ' + module.__name__
    if type(object) is type(_OldStyleClass()):
        # If the passed object is an instance of an old-style class,
        # document its available methods instead of its value.
        object = object.__class__
    elif not (inspect.ismodule(object) or
              inspect.isclass(object) or
              inspect.isroutine(object) or
              inspect.isgetsetdescriptor(object) or
              inspect.ismemberdescriptor(object) or
              isinstance(object, property)):
        # If the passed object is a piece of data or an instance,
        # document its available methods instead of its value.
        object = type(object)
        desc += ' object'
    return title % desc + '\n\n' + pydoc.text.document(object, name)


class MainHandler(webapp.RequestHandler):

  def get(self):
    self.response.out.write("""
    <h1>Google API Client for Python Documentation</h1>
    <ul>
      <li><a href='/buzz/v1'>buzz</a>
      <li><a href='/moderator/v1'>moderator</a>
      <li><a href='/latitude/v1'>latitude</a>
    </ul>
    """)

class ServiceHandler(webapp.RequestHandler):

  def get(self, service_name, version):
    service = build(service_name, version)
    page = "<p><a href='/'>Home</a></p><pre>%s</pre>" % pydoc.plain(render_doc(service))

    collections = []
    for name in dir(service):
      if not "_" in name and callable(getattr(service, name)):
        collections.append(name)

    for name in collections:
      page = re.sub('(%s) =' % name, r'<a href="/%s/%s/%s">\1</a> =' % (service_name, version, name), page)

    self.response.out.write(page)

class CollectionHandler(webapp.RequestHandler):

  def get(self, service_name, version, collection):
    service = build(service_name, version)
    page = "<p><a href='/'>Home</a></p><pre>%s</pre>" % pydoc.plain(render_doc(getattr(service, collection)()))
    self.response.out.write(page)

def main():
  application = webapp.WSGIApplication(
      [
      (r'/', MainHandler),
      (r'/(\w*)/(\w*)', ServiceHandler),
      (r'/(\w*)/(\w*)/(\w*)', CollectionHandler),
      ],
      debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
