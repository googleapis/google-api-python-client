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
import logging
import os
import pydoc
import re

import describe
import uritemplate

from apiclient import discovery
from apiclient.errors import HttpError
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util
from oauth2client.anyjson import simplejson


DISCOVERY_URI = 'https://www.googleapis.com/discovery/v1/apis?preferred=true'


def get_directory_doc():
  http = httplib2.Http(memcache)
  ip = os.environ.get('REMOTE_ADDR', None)
  uri = DISCOVERY_URI
  if ip:
    uri += ('&userIp=' + ip)
  resp, content = http.request(uri)
  directory = simplejson.loads(content)['items']
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

    real_version = describe.unsafe_version(version)

    logging.info('%s %s %s', service_name, version, collection)
    http = httplib2.Http(memcache)
    try:
      resource = discovery.build(service_name, real_version, http=http)
    except:
      logging.error('Failed to build service.')
      return self.error(404)

    DISCOVERY_URI = ('https://www.googleapis.com/discovery/v1/apis/'
      '{api}/{apiVersion}/rest')
    response, content = http.request(
        uritemplate.expand(
            DISCOVERY_URI, {
                'api': service_name,
                'apiVersion': real_version})
            )
    root_discovery = simplejson.loads(content)
    collection_discovery = root_discovery

    # descend the object path
    if collection:
      try:
        path = collection.split('.')
        if path:
          for method in path:
            resource = getattr(resource, method)()
            collection_discovery = collection_discovery['resources'][method]
      except:
        logging.error('Failed to parse the collections.')
        return self.error(404)
    logging.info('Built everything successfully so far.')

    path = '%s_%s.' % (service_name, version)
    if collection:
      path += '.'.join(collection.split('/'))
      path += '.'

    page = describe.document_collection(
        resource, path, root_discovery, collection_discovery)

    self.response.out.write(page)


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
