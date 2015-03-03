#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright 2014 Google Inc. All Rights Reserved.
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
from __future__ import print_function

__author__ = 'zachn@google.com (Zach Newell)'

import argparse
import pprint
import sys

from oauth2client import client
from googleapiclient import sample_tools

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('teamId', help='Coordinate Team ID')


def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'coordinate', 'v1', __doc__, __file__, parents=[argparser],
      scope='https://www.googleapis.com/auth/coordinate')

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
      teamId=flags.teamId,
      address='1600 Amphitheatre Parkway Mountain View, CA 94043',
      lat='37.422120',
      lng='122.084429',
      assignee=None,
      note=note).execute()

    pprint.pprint(insert_result)

    # Close the job
    update_result = service.jobs().update(body='',
      teamId=flags.teamId,
      jobId=insert_result['id'],
      progress='COMPLETED').execute()

    pprint.pprint(update_result)

  except AccessTokenRefreshError as e:
    print ('The credentials have been revoked or expired, please re-run'
      'the application to re-authorize')


if __name__ == '__main__':
  main(sys.argv)
