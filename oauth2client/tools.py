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

"""Command-line tools for authenticating via OAuth 2.0

Do the OAuth 2.0 Web Server dance for
a command line application. Stores the generated
credentials in a common file that is used by
other example apps in the same directory.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'
__all__ = ["run"]

import socket
import sys
import BaseHTTPServer
import logging

from optparse import OptionParser
from oauth2client.file import Storage

try:
    from urlparse import parse_qsl
except ImportError:
    from cgi import parse_qsl

# TODO(jcgregorio)
#  - docs
#  - error handling
#  - oob when implemented


class ClientRedirectServer(BaseHTTPServer.HTTPServer):
  """A server to handle OAuth 2.0 redirects back to localhost.

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

    Checks the query parameters and if an error
    occurred print a message of failure, otherwise
    indicate success.
    """
    s.send_response(200)
    s.send_header("Content-type", "text/html")
    s.end_headers()
    query = s.path.split('?', 1)[-1]
    query = dict(parse_qsl(query))
    s.server.query_params = query
    s.wfile.write("<html><head><title>Authentication Status</title></head>")
    if 'error' in query:
      s.wfile.write("<body><p>The authentication request failed.</p>")
    else:
      s.wfile.write("<body><p>You have successfully authenticated</p>")
    s.wfile.write("</body></html>")

  def log_message(self, format, *args):
    """Do not log messages to stdout while running as a command line program."""
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

  authorize_url = flow.step1_get_authorize_url('http://%s:%s/' % (host_name, port_number))

  print 'Go to the following link in your browser:'
  print authorize_url
  print

  if options.localhost:
    httpd.handle_request()
    if 'error' in httpd.query_params:
      sys.exit('Authentication request was rejected.')
    if 'code' in httpd.query_params:
      code = httpd.query_params['code']
  else:
    accepted = 'n'
    while accepted.lower() == 'n':
      accepted = raw_input('Have you authorized me? (y/n) ')
    code = raw_input('What is the verification code? ').strip()

  credentials = flow.step2_exchange(code)

  Storage(options.filename).put(credentials)
  print "You have successfully authenticated."
