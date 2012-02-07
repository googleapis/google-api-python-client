#!/usr/bin/python
#
# Copyright 2011 Google Inc. All Rights Reserved.
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

"""Auxiliary file for AdSense Management API code samples.

Handles various tasks to do with logging, authentication and initialization.
"""

__author__ = 'sergio.gomes@google.com (Sergio Gomes)'

import logging
import os
import sys
from apiclient.discovery import build
import gflags
import httplib2
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

# Set up a Flow object to be used if we need to authenticate.
FLOW = flow_from_clientsecrets(CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/adsense.readonly',
    message=MISSING_CLIENT_SECRETS_MESSAGE)

# The gflags module makes defining command-line options easy for applications.
# Run this program with the '--help' argument to see all the flags that it
# understands.
gflags.DEFINE_enum('logging_level', 'ERROR',
                   ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                   'Set the level of logging detail.')


def process_flags(argv):
  """Uses the command-line flags to set the logging level."""

  # Let the gflags module process the command-line arguments.
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError, e:
    print '%s\nUsage: %s ARGS\n%s' % (e, argv[0], FLAGS)
    sys.exit(1)

  # Set the logging according to the command-line flag.
  logging.getLogger().setLevel(getattr(logging, FLAGS.logging_level))


def prepare_credentials():
  """Handles auth. Reuses credentialss if available or runs the auth flow."""

  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # Credentials will get written back to a file.
  storage = Storage('adsense.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = run(FLOW, storage)
  return credentials


def retrieve_service(http):
  """Retrieves an AdSense Management API service via the discovery service."""

  # Construct a service object via the discovery service.
  service = build("adsense", "v1.1", http=http)
  return service


def initialize_service():
  """Builds instance of service from discovery data and does auth."""

  # Create an httplib2.Http object to handle our HTTP requests.
  http = httplib2.Http()

  # Prepare credentials, and authorize HTTP object with them.
  credentials = prepare_credentials()
  http = credentials.authorize(http)

  # Retrieve service.
  return retrieve_service(http)
