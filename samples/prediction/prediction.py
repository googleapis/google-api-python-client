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
  $ python prediction.py --object_name="bucket/object" --id="model_id"

You can also get help on all the command-line flags the program understands
by running:

  $ python prediction.py --help

To get detailed log output run:

  $ python prediction.py --logging_level=DEBUG
"""

__author__ = ('jcgregorio@google.com (Joe Gregorio), '
              'marccohen@google.com (Marc Cohen)')

import argparse
import os
import pprint
import sys
import time

from apiclient import discovery
from apiclient import sample_tools
from oauth2client import client


# Time to wait (in seconds) between successive checks of training status.
SLEEP_TIME = 10


# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('object_name',
                     help='Full Google Storage path of csv data (ex bucket/object)')
argparser.add_argument('id',
                     help='Model Id of your choosing to name trained model')


def print_header(line):
  '''Format and print header block sized to length of line'''
  header_str = '='
  header_line = header_str * len(line)
  print '\n' + header_line
  print line
  print header_line


def main(argv):
  service, flags = sample_tools.init(
      argv, 'prediction', 'v1.5', __doc__, __file__, parents=[argparser],
      scope='https://www.googleapis.com/auth/prediction')

  try:
    # Get access to the Prediction API.
    papi = service.trainedmodels()

    # List models.
    print_header('Fetching list of first ten models')
    result = papi.list(maxResults=10).execute()
    print 'List results:'
    pprint.pprint(result)

    # Start training request on a data set.
    print_header('Submitting model training request')
    body = {'id': flags.id, 'storageDataLocation': flags.object_name}
    start = papi.insert(body=body).execute()
    print 'Training results:'
    pprint.pprint(start)

    # Wait for the training to complete.
    print_header('Waiting for training to complete')
    while True:
      status = papi.get(id=flags.id).execute()
      state = status['trainingStatus']
      print 'Training state: ' + state
      if state == 'DONE':
        break
      elif state == 'RUNNING':
        time.sleep(SLEEP_TIME)
        continue
      else:
        raise Exception('Training Error: ' + state)

      # Job has completed.
      print 'Training completed:'
      pprint.pprint(status)
      break

    # Describe model.
    print_header('Fetching model description')
    result = papi.analyze(id=flags.id).execute()
    print 'Analyze results:'
    pprint.pprint(result)

    # Make a prediction using the newly trained model.
    print_header('Making a prediction')
    body = {'input': {'csvInstance': ["mucho bueno"]}}
    result = papi.predict(body=body, id=flags.id).execute()
    print 'Prediction results...'
    pprint.pprint(result)

    # Delete model.
    print_header('Deleting model')
    result = papi.delete(id=flags.id).execute()
    print 'Model deleted.'

  except client.AccessTokenRefreshError:
    print ("The credentials have been revoked or expired, please re-run"
      "the application to re-authorize")


if __name__ == '__main__':
  main(sys.argv)
