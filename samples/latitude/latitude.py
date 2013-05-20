#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Google Inc.
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

"""Simple command-line example for Latitude.

Command-line application that sets the users
current location.

Usage:
  $ python latitude.py

You can also get help on all the command-line flags the program understands
by running:

  $ python latitude.py --help

To get detailed log output run:

  $ python latitude.py --logging_level=DEBUG
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import sys

from oauth2client import client
from apiclient import sample_tools

def main(argv):
  service, flags = sample_tools.init(
      argv, 'latitude', 'v1', __doc__, __file__,
      scope='https://www.googleapis.com/auth/latitude.all.best')

  try:
    body = {
        "data": {
            "kind": "latitude#location",
            "latitude": 37.420352,
            "longitude": -122.083389,
            "accuracy": 130,
            "altitude": 35
            }
        }

    print service.currentLocation().insert(body=body).execute()

  except client.AccessTokenRefreshError:
    print ("The credentials have been revoked or expired, please re-run"
      "the application to re-authorize")

if __name__ == '__main__':
  main(sys.argv)
