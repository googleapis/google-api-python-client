#!/usr/bin/python
#
# Copyright 2014 Google Inc. All Rights Reserved.
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

"""Gets all alerts available for the logged in user's account.

Tags: alerts.list
"""
from __future__ import print_function

__author__ = 'sgomes@google.com (Sérgio Gomes)'

import argparse
import sys

from googleapiclient import sample_tools
from oauth2client import client


def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'adexchangeseller', 'v1.1', __doc__, __file__, parents=[],
      scope='https://www.googleapis.com/auth/adexchange.seller.readonly')

  try:
    # Retrieve alerts list in pages and display data as we receive it.
    request = service.alerts().list()

    if request is not None:
      result = request.execute()
      if 'items' in result:
        alerts = result['items']
        for alert in alerts:
          print(('Alert id "%s" with severity "%s" and type "%s" was found. '
                 % (alert['id'], alert['severity'], alert['type'])))
      else:
        print('No alerts found!')
  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
