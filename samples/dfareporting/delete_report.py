#!/usr/bin/python
#
# Copyright 2013 Google Inc. All Rights Reserved.
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

"""This example illustrates how to delete a report.

Tags: reports.delete
"""

__author__ = ('jimper@google.com (Jonathon Imperiosi)')

import argparse
import pprint
import sys

from googleapiclient import sample_tools
from oauth2client import client

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('profile_id', type=int,
                     help='The ID of the profile to delete a report for')
argparser.add_argument('report_id', type=int,
                     help='The ID of the report to delete')


def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'dfareporting', 'v1.3', __doc__, __file__, parents=[argparser],
      scope='https://www.googleapis.com/auth/dfareporting')

  profile_id = flags.profile_id
  report_id = flags.report_id

  try: 
    # Construct the request.
    request = service.reports().delete(profileId=profile_id, reportId=report_id)

    # Execute request and print response.
    pprint.pprint(request.execute())
  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)