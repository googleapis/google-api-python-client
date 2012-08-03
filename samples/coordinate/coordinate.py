#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
#  Copyright 2012 Google Inc. All Rights Reserved.
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

"""Simple command-line sample for Google Coordinate.

Pulls a list of jobs, creates a job and marks a job complete for a given
Coordinate team. Client IDs for installed applications are created in the
Google API Console. See the documentation for more information:

   https://developers.google.com/console/help/#WhatIsKey

Usage:
  $ python coordinate.py -t teamId

You can also get help on all the command-line flags the program understands
by running:

  $ python coordinate.py --help

To get detailed log output run:

  $ python coordinate.py -t teamId --logging_level=DEBUG
"""

__author__ = 'zachn@google.com (Zach Newell)'

import gflags
import httplib2
import logging
import os
import pprint
import sys

from apiclient.discovery import build
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run


FLAGS = gflags.FLAGS


# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found
# on the API Access tab on the Google APIs
# Console <http://code.google.com/apis/console>
CLIENT_SECRETS = 'client_secrets.json'

# Helpful message to display in the browser if the CLIENT_SECRETS file
# is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the APIs Console <https://code.google.com/apis/console>.

""" % os.path.join(os.path.dirname(__file__), CLIENT_SECRETS)

FLOW = flow_from_clientsecrets(CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/coordinate',
    message=MISSING_CLIENT_SECRETS_MESSAGE)


# The gflags module makes defining command-line options easy for
# applications. Run this program with the '--help' argument to see
# all the flags that it understands.
gflags.DEFINE_enum('logging_level', 'ERROR',
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    'Set the level of logging detail.')

gflags.DEFINE_string('teamId', None, 'Coordinate Team ID', short_name='t')

# Create a validator for the teamId flag.
gflags.RegisterValidator('teamId',
    lambda value: value is not None,
    message='--teamId must be defined.',
    flag_values=FLAGS)

# Make the flag mandatory
gflags.MarkFlagAsRequired('teamId')


def main(argv):
  # Let the gflags module process the command-line arguments
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
  storage = Storage('coordinate.dat')
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run(FLOW, storage)

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  http = httplib2.Http()
  http = credentials.authorize(http)

  service = build('coordinate', 'v1', http=http)

  try:
    # List all the jobs for a team
    jobs_result = service.jobs().list(teamId=FLAGS.teamId).execute(http=http)

    print('List of Jobs:')
    pprint.pprint(jobs_result)

    # Multiline note
    note = """
    These are notes...
    on different lines
    """

    # Insert a job and store the results
    insert_result = service.jobs().insert(body='',
      title='Google Campus',
      teamId=FLAGS.teamId,
      address='1600 Amphitheatre Parkway Mountain View, CA 94043',
      lat='37.422120',
      lng='122.084429',
      assignee=None,
      note=note).execute()

    pprint.pprint(insert_result)

    # Close the job
    update_result = service.jobs().update(body='',
      teamId=FLAGS.teamId,
      jobId=insert_result['id'],
      progress='COMPLETED').execute()

    pprint.pprint(update_result)

  except AccessTokenRefreshError, e:
    print ('The credentials have been revoked or expired, please re-run'
      'the application to re-authorize')


if __name__ == '__main__':
  main(sys.argv)
