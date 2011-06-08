#!/usr/bin/env python
#
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

"""Class to connect to TaskQueue API."""



import os
import sys
import urlparse
from apiclient.anyjson import simplejson as json
from apiclient.discovery import build
from apiclient.errors import HttpError
import httplib2
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run
from gtaskqueue.taskqueue_logger import logger

from google.apputils import app
import gflags as flags

FLAGS = flags.FLAGS
flags.DEFINE_string(
        'service_version',
        'v1beta1',
        'Google taskqueue api version.')
flags.DEFINE_string(
        'api_host',
        'https://www.googleapis.com/',
        'API host name')
flags.DEFINE_bool(
        'use_developer_key',
        False,
        'User wants to use the developer key while accessing taskqueue apis')
flags.DEFINE_string(
        'developer_key_file',
        '~/.taskqueue.apikey',
        'Developer key provisioned from api console')
flags.DEFINE_bool(
        'dump_request',
        False,
        'Prints the outgoing HTTP request along with headers and body.')
flags.DEFINE_string(
        'credentials_file',
        'taskqueue.dat',
        'File where you want to store the auth credentails for later user')

# Set up a Flow object to be used if we need to authenticate. This
# sample uses OAuth 2.0, and we set up the OAuth2WebServerFlow with
# the information it needs to authenticate. Note that it is called
# the Web Server Flow, but it can also handle the flow for native
# applications <http://code.google.com/apis/accounts/docs/OAuth2.html#IA>
# The client_id client_secret are copied from the Identity tab on
# the Google APIs Console <http://code.google.com/apis/console>
FLOW = OAuth2WebServerFlow(
    client_id='157776985798.apps.googleusercontent.com',
    client_secret='tlpVCmaS6yLjxnnPu0ARIhNw',
    scope='https://www.googleapis.com/auth/taskqueue',
    user_agent='taskqueue-cmdline-sample/1.0')


class TaskQueueClient:
    """Class to setup connection with taskqueue API."""

    def __init__(self):
        if not FLAGS.project_name:
            raise app.UsageError('You must specify a project name'
                                 ' using the "--project_name" flag.')
        discovery_uri = (
            FLAGS.api_host + 'discovery/v1/apis/{api}/{apiVersion}/rest')
        logger.info(discovery_uri)
        try:
            # If the Credentials don't exist or are invalid run through the
            # native clien flow. The Storage object will ensure that if
            # successful the good Credentials will get written back to a file.
            # Setting FLAGS.auth_local_webserver to false since we can run our
            # tool on Virtual Machines and we do not want to run the webserver
            # on VMs.
            FLAGS.auth_local_webserver = False
            storage = Storage(FLAGS.credentials_file)
            credentials = storage.get()
            if credentials is None or credentials.invalid == True:
                credentials = run(FLOW, storage)
            http = credentials.authorize(self._dump_request_wrapper(
                    httplib2.Http()))
            self.task_api = build('taskqueue',
                                  FLAGS.service_version,
                                  http=http,
                                  discoveryServiceUrl=discovery_uri)
        except HttpError, http_error:
            logger.error('Error gettin task_api: %s' % http_error)

    def get_taskapi(self):
        """Returns handler for tasks  API from taskqueue API collection."""
        return self.task_api


    def _dump_request_wrapper(self, http):
        """Dumps the outgoing HTTP request if requested.

        Args:
            http: An instance of httplib2.Http or something that acts like it.

        Returns:
            httplib2.Http like object.
        """
        request_orig = http.request

        def new_request(uri, method='GET', body=None, headers=None,
                        redirections=httplib2.DEFAULT_MAX_REDIRECTS,
                        connection_type=None):
            """Overrides the http.request method to add some utilities."""
            if (FLAGS.api_host + "discovery/" not in uri and
                FLAGS.use_developer_key):
                developer_key_path = os.path.expanduser(
                    FLAGS.developer_key_file)
                if not os.path.isfile(developer_key_path):
                    print 'Please generate developer key from the Google API' \
                    'Console and store it in %s' % (FLAGS.developer_key_file)
                    sys.exit()
                developer_key_file = open(developer_key_path, 'r')
                try:
                    developer_key = developer_key_file.read().strip()
                except IOError, io_error:
                    print 'Error loading developer key from file %s' % (
                            FLAGS.developer_key_file)
                    print 'Error details: %s' % str(io_error)
                    sys.exit()
                finally:
                    developer_key_file.close()
                s = urlparse.urlparse(uri)
                query = 'key=' + developer_key
                if s.query:
                    query = s.query + '&key=' + developer_key
                d = urlparse.ParseResult(s.scheme,
                                         s.netloc,
                                         s.path,
                                         s.params,
                                         query,
                                         s.fragment)
                uri = urlparse.urlunparse(d)
            if FLAGS.dump_request:
                print '--request-start--'
                print '%s %s' % (method, uri)
                if headers:
                    for (h, v) in headers.iteritems():
                        print '%s: %s' % (h, v)
                print ''
                if body:
                    print json.dumps(json.loads(body),
                                     sort_keys=True,
                                     indent=2)
                print '--request-end--'
            return request_orig(uri,
                                method,
                                body,
                                headers,
                                redirections,
                                connection_type)
        http.request = new_request
        return http

    def print_result(self, result):
        """Pretty-print the result of the command.

        The default behavior is to dump a formatted JSON encoding
        of the result.

        Args:
            result: The JSON-serializable result to print.
        """
        # We could have used the pprint module, but it produces
        # noisy output due to all of our keys and values being
        # unicode strings rather than simply ascii.
        print json.dumps(result, sort_keys=True, indent=2)
