#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from __future__ import print_function

__author__ = 'rahulpaul@google.com (Rahul Paul)'

import pprint
import re
import sys

from oauth2client import client
from googleapiclient import sample_tools


def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'audit', 'v1', __doc__, __file__,
      scope='https://www.googleapis.com/auth/apps/reporting/audit.readonly')

  try:
    activities = service.activities()

    # Retrieve the first two activities
    print('Retrieving the first 2 activities...')
    activity_list = activities.list(
        applicationId='207535951991', customerId='C01rv1wm7', maxResults='2',
        actorEmail='admin@enterprise-audit-clientlib.com').execute()
    pprint.pprint(activity_list)

    # Now retrieve the next 2 events
    match = re.search('(?<=continuationToken=).+$', activity_list['next'])
    if match is not None:
      next_token = match.group(0)

      print('\nRetrieving the next 2 activities...')
      activity_list = activities.list(
          applicationId='207535951991', customerId='C01rv1wm7',
          maxResults='2', actorEmail='admin@enterprise-audit-clientlib.com',
          continuationToken=next_token).execute()
      pprint.pprint(activity_list)

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run'
      'the application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)

