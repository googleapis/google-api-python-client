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

"""This example retrieves a report for the specified ad client.

To get ad clients, run get_all_ad_clients.py.

Tags: reports.generate
"""

__author__ = 'sergio.gomes@google.com (Sergio Gomes)'

import sys
import gflags
from oauth2client.client import AccessTokenRefreshError
import sample_utils

# Declare command-line flags, and set them as required.
gflags.DEFINE_string('ad_client_id', None,
                     'The ID of the ad client for which to generate a report',
                     short_name='c')
gflags.MarkFlagAsRequired('ad_client_id')


def main(argv):
  # Process flags and read their values.
  sample_utils.process_flags(argv)
  ad_client_id = gflags.FLAGS.ad_client_id

  # Authenticate and construct service.
  service = sample_utils.initialize_service()

  try:
    # Retrieve report.
    result = service.reports().generate(
        startDate='2011-01-01', endDate='2011-08-31',
        filter=['AD_CLIENT_ID==' + ad_client_id],
        metric=['PAGE_VIEWS', 'AD_REQUESTS', 'AD_REQUESTS_COVERAGE',
                'CLICKS', 'AD_REQUESTS_CTR', 'COST_PER_CLICK',
                'AD_REQUESTS_RPM', 'EARNINGS'],
        dimension=['DATE'],
        sort=['+DATE']).execute()

    # Display headers.
    for header in result['headers']:
      print '%25s' % header['name'],
    print

    # Display results.
    for row in result['rows']:
      for column in row:
        print '%25s' % column,
      print

  except AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
