#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
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

"""Simple command-line sample for the Google Prediction API

Command-line application that trains on your input data. This sample does
the same thing as the Hello Prediction! example. You might want to run
the setup.sh script to load the sample data to Google Storage.

Usage:
  $ python prediction_language_id.py --model_id="foo" 
    --data_file="bucket/object"

You can also get help on all the command-line flags the program understands
by running:

  $ python prediction_language_id.py --help

To get detailed log output run:

  $ python prediction_language_id.py --logging_level=DEBUG
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

from apiclient.discovery import build_from_document

import apiclient.errors
import gflags
import httplib2
import logging
import os
import pprint
import sys

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import flow_from_clientsecrets
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
    scope='https://www.googleapis.com/auth/prediction',
    message=MISSING_CLIENT_SECRETS_MESSAGE)

# The gflags module makes defining command-line options easy for
# applications. Run this program with the '--help' argument to see
# all the flags that it understands.
gflags.DEFINE_enum('logging_level', 'ERROR',
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    'Set the level of logging detail.')

gflags.DEFINE_string('model_id',
                     None,
                     'The unique name for the predictive model (ex foo)')

gflags.DEFINE_string('data_file',
                     None,
                     'Full Google Storage path of csv data (ex bucket/object)')

gflags.MarkFlagAsRequired('model_id')
gflags.MarkFlagAsRequired('data_file')

def main(argv):
  # Let the gflags module process the command-line arguments
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError, e:
    print '%s\\nUsage: %s ARGS\\n%s' % (e, argv[0], FLAGS)
    sys.exit(1)

  # Set the logging according to the command-line flag
  logging.getLogger().setLevel(getattr(logging, FLAGS.logging_level))

  # If the Credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # Credentials will get written back to a file.
  storage = Storage('prediction.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = run(FLOW, storage)

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  http = httplib2.Http()
  http = credentials.authorize(http)

  service = build("prediction", "v1.4", http=http)

  try:

    # Start training on a data set
    train = service.trainedmodels()
    body = {'id': FLAGS.model_id, 'storageDataLocation': FLAGS.data_file}
    start = train.insert(body=body).execute()

    print 'Started training'
    pprint.pprint(start)

    import time
    # Wait for the training to complete
    while True:
      try:
        # We check the training job is completed. If it is not it will return
        # an error code.
        status = train.get(id=FLAGS.model_id).execute()
        # Job has completed.
        pprint.pprint(status)
        break
      except apiclient.errors.HttpError as error:
        # Training job not yet completed.
        print 'Waiting for training to complete.'
        time.sleep(10)

    print 'Training is complete'

    # Now make a prediction using that training
    body = {'input': {'csvInstance': ["mucho bueno"]}}
    prediction = train.predict(body=body, id=FLAGS.model_id).execute()
    print 'The prediction is:'
    pprint.pprint(prediction)


  except AccessTokenRefreshError:
    print ("The credentials have been revoked or expired, please re-run"
      "the application to re-authorize")

if __name__ == '__main__':
  main(sys.argv)

