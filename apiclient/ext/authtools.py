# Copyright (C) 2010 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Command-line tools for authenticating via OAuth 1.0

Do the OAuth 1.0 Three Legged Dance for
a command line application. Stores the generated
credentials in a common file that is used by
other example apps in the same directory.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'
__all__ = ["run"]

import BaseHTTPServer
import logging
import pickle
import socket
import sys

from optparse import OptionParser
from apiclient.oauth import RequestError

try:
    from urlparse import parse_qsl
except ImportError:
    from cgi import parse_qsl


class ClientRedirectServer(BaseHTTPServer.HTTPServer):
  """A server to handle OAuth 1.0 redirects back to localhost.

  Waits for a single request and parses the query parameters
  into query_params and then stops serving.
  """
  query_params = {}


class ClientRedirectHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  """A handler for OAuth 2.0 redirects back to localhost.

  Waits for a single request and parses the query parameters
  into the servers query_params and then stops serving.
  """

  def do_GET(s):
    """Handle a GET request

    Parses the query parameters and prints a message
    if the flow has completed. Note that we can't detect
    if an error occurred.
    """
    s.send_response(200)
    s.send_header("Content-type", "text/html")
    s.end_headers()
    query = s.path.split('?', 1)[-1]
    query = dict(parse_qsl(query))
    s.server.query_params = query
    s.wfile.write("<html><head><title>Authentication Status</title></head>")
    s.wfile.write("<body><p>The authentication flow has completed.</p>")
    s.wfile.write("</body></html>")

  def log_message(self, format, *args):
    """Do not log messages to stdout while running as command line program."""
    pass


def run(flow, filename):
  """Core code for a command-line application.
  """
  parser = OptionParser()
  parser.add_option("-f", "--file", dest="filename",
      default=filename, help="write credentials to FILE", metavar="FILE")
  parser.add_option("-p", "--no_local_web_server", dest="localhost",
      action="store_false",
      default=True,
      help="Do not run a web server on localhost to handle redirect URIs")
  parser.add_option("-w", "--local_web_server", dest="localhost",
      action="store_true",
      default=True,
      help="Run a web server on localhost to handle redirect URIs")

  (options, args) = parser.parse_args()

  host_name = 'localhost'
  port_numbers = [8080, 8090]
  if options.localhost:
    server_class = BaseHTTPServer.HTTPServer
    try:
      port_number = port_numbers[0]
      httpd = server_class((host_name, port_number), ClientRedirectHandler)
    except socket.error:
      port_number = port_numbers[1]
      try:
        httpd = server_class((host_name, port_number), ClientRedirectHandler)
      except socket.error:
        options.localhost = False

  if options.localhost:
    oauth_callback = 'http://%s:%s/' % (host_name, port_number)
  else:
    oauth_callback = 'oob'
  authorize_url = flow.step1_get_authorize_url(oauth_callback)

  print 'Go to the following link in your browser:'
  print authorize_url
  print

  if options.localhost:
    httpd.handle_request()
    if 'error' in httpd.query_params:
      sys.exit('Authentication request was rejected.')
    if 'oauth_verifier' in httpd.query_params:
      code = httpd.query_params['oauth_verifier']
  else:
    accepted = 'n'
    while accepted.lower() == 'n':
      accepted = raw_input('Have you authorized me? (y/n) ')
    code = raw_input('What is the verification code? ').strip()

  try:
    credentials = flow.step2_exchange(code)
  except RequestError:
    sys.exit('The authentication has failed.')

  f = open(filename, 'w')
  f.write(pickle.dumps(credentials))
  f.close()
  print "You have successfully authenticated."
