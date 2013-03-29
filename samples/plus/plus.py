#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Google Inc.
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

"""Simple command-line sample for the Google+ API.

Command-line application that retrieves the list of the user's posts."""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import argparse
import logging
import os
import sys

import httplib2

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools


# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found
# on the API Access tab on the Google APIs
# Console <http://code.google.com/apis/console>.
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

# Set up a Flow object to be used if we need to authenticate.
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/plus.me',
    message=tools.message_if_missing(CLIENT_SECRETS))


def main(argv):
  # Parse command-line options.
  parser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter,
      parents=[tools.argparser])
  flags = parser.parse_args(argv[1:])

  # If the Credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # Credentials will get written back to a file.
  storage = file.Storage('plus.dat')
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = tools.run(FLOW, storage, flags)

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  http = credentials.authorize(httplib2.Http())

  service = discovery.build('plus', 'v1', http=http)

  try:
    person = service.people().get(userId='me').execute()

    print 'Got your ID: %s' % person['displayName']
    print
    print '%-040s -> %s' % ('[Activitity ID]', '[Content]')

    # Don't execute the request until we reach the paging loop below.
    request = service.activities().list(
        userId=person['id'], collection='public')

    # Loop over every activity and print the ID and a short snippet of content.
    while request is not None:
      activities_doc = request.execute()
      for item in activities_doc.get('items', []):
        print '%-040s -> %s' % (item['id'], item['object']['content'][:30])

      request = service.activities().list_next(request, activities_doc)

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run'
      'the application to re-authorize.')

if __name__ == '__main__':
  main(sys.argv)
