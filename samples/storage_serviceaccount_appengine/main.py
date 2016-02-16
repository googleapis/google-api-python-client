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
"""This application produces formatted listings for Google Cloud
   Storage buckets.

It takes a bucket name in the URL path and does an HTTP GET on the
corresponding Google Cloud Storage URL to obtain a listing of the bucket
contents. For example, if this app is invoked with the URI
http://bucket-list.appspot.com/foo, it would remove the bucket name 'foo',
append it to the Google Cloud Storage service URI and send a GET request to
the resulting URI. The bucket listing is returned in an XML document, which is
prepended with a reference to an XSLT style sheet for human readable
presentation.

More information about using Google App Engine apps and service accounts to
call Google APIs can be found here:

<https://developers.google.com/accounts/docs/OAuth2ServiceAccount>
<http://code.google.com/appengine/docs/python/appidentity/overview.html>
"""

__author__ = 'marccohen@google.com (Marc Cohen)'

import httplib2
import logging
import os
import pickle
import re

from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from oauth2client.contrib.appengine import AppAssertionCredentials

# Constants for the XSL stylesheet and the Google Cloud Storage URI.
XSL = '\n<?xml-stylesheet href="/listing.xsl" type="text/xsl"?>\n';
URI = 'http://commondatastorage.googleapis.com'

# Obtain service account credentials and authorize HTTP connection.
credentials = AppAssertionCredentials(
    scope='https://www.googleapis.com/auth/devstorage.read_write')
http = credentials.authorize(httplib2.Http(memcache))


class MainHandler(webapp.RequestHandler):

  def get(self):
    try:
      # Derive desired bucket name from path after domain name.
      bucket = self.request.path
      if bucket[-1] == '/':
        # Trim final slash, if necessary.
        bucket = bucket[:-1]
      # Send HTTP request to Google Cloud Storage to obtain bucket listing.
      resp, content = http.request(URI + bucket, "GET")
      if resp.status != 200:
        # If error getting bucket listing, raise exception.
        err = 'Error: ' + str(resp.status) + ', bucket: ' + bucket + \
              ', response: ' + str(content)
        raise Exception(err)
      # Edit returned bucket listing XML to insert a reference to our style
      # sheet for nice formatting and send results to client.
      content = re.sub('(<ListBucketResult)', XSL + '\\1', content)
      self.response.headers['Content-Type'] = 'text/xml'
      self.response.out.write(content)
    except Exception as e:
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.set_status(404)
      self.response.out.write(str(e))


def main():
  application = webapp.WSGIApplication(
      [
       ('.*', MainHandler),
      ],
      debug=True)
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
