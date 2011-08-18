#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Google Inc.
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

"""Simple command-line sample for Audit API.

Command-line application that retrieves events through the Audit API.
This works only for Google Apps for Business, Education, and ISP accounts.
It can not be used for the basic Google Apps product.

Usage:
  $ python audit.py

You can also get help on all the command-line flags the program understands
by running:

  $ python audit.py --help

To get detailed log output run:

  $ python audit.py --logging_level=DEBUG
"""

__author__ = 'rahulpaul@google.com (Rahul Paul)'

import gflags
import httplib2
import logging
import re
import simplejson
import sys

from apiclient.discovery import build
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from oauth2client.tools import run

FLAGS = gflags.FLAGS

# Set up a Flow object to be used if we need to authenticate. This
# sample uses OAuth 2.0, and we set up the OAuth2WebServerFlow with
# the information it needs to authenticate. Note that it is called
# the Web Server Flow, but it can also handle the flow for native
# applications <http://code.google.com/apis/accounts/docs/OAuth2.html#IA>
# When creating credentials for this application be sure to choose an
# Application type of 'Installed application'.
FLOW = OAuth2WebServerFlow(
    client_id='880851855448.apps.googleusercontent.com',
    client_secret='d8nBjlNBpOMH_LITqz31IMdI',
    scope='https://www.googleapis.com/auth/apps/reporting/audit.readonly',
    user_agent='audit-cmdline-sample/1.0')

# The flags module makes defining command-line options easy for
# applications. Run this program with the '--help' argument to see
# all the flags that it understands.
gflags.DEFINE_enum('logging_level', 'ERROR',
                  ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                  'Set the level of logging detail.')


def print_activities(activity_list):
  events = activity_list['items']
  print '\nRetrieved %d activities.' % len(events)
  for i in range(len(events)):
    print '\nEvent %d : %s' % (i, simplejson.JSONEncoder().encode(events[i]))
  print '\nNext URL : %s' % (activity_list['next'])
  print '======================================================================'


def main(argv):
  # Let the flags module process the command-line arguments
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError, e:
    print '%s\nUsage: %s ARGS\n%s' % (e, argv[0], FLAGS)
    sys.exit(1)

  # Set the logging according to the command-line flag
  logging.getLogger().setLevel(getattr(logging, FLAGS.logging_level))

  # If the Credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # Credentials will get written back to a file.
  storage = Storage('audit.dat')
  credentials = storage.get()
  if not credentials or credentials.invalid:
    credentials = run(FLOW, storage)

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  http = httplib2.Http()
  http = credentials.authorize(http)

  service = build('audit', 'v1', http=http)

  try:
    activities = service.activities()

    # Retrieve the first two activities
    print 'Retrieving the first 2 activities...'
    activity_list = activities.list(
        applicationId='207535951991', customerId='C01rv1wm7', maxResults='2',
        actorEmail='admin@enterprise-audit-clientlib.com').execute()
    print_activities(activity_list)

    # Now retrieve the next 2 events
    match = re.search('(?<=continuationToken=).+$', activity_list['next'])
    if match is not None:
      next_token = match.group(0)

      print '\nRetrieving the next 2 activities...'
      activity_list = activities.list(
          applicationId='207535951991', customerId='C01rv1wm7',
          maxResults='2', actorEmail='admin@enterprise-audit-clientlib.com',
          continuationToken=next_token).execute()
      print_activities(activity_list)

  except AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run'
           'the application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
