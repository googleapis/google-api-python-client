#!/usr/bin/python
#
# Copyright 2012 Google Inc. All Rights Reserved.
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

"""This example retrieves a report for the specified publisher ad client.

Note that the statistics returned in these reports only include data from ad
units created with the AdSense Host API v4.x.
To create ad units, run add_ad_unit_to_publisher.py.
To get ad clients, run get_all_ad_clients_for_publisher.py.

Tags: accounts.reports.generate
"""

__author__ = 'jalc@google.com (Jose Alcerreca)'

import argparse
import sys

from apiclient import sample_tools
from oauth2client import client

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument(
    'account_id',
    help='The ID of the publisher account for which to generate a report')
argparser.add_argument(
    'ad_client_id',
    help='The ID of the ad client for which to generate a report')


def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'adsensehost', 'v4.1', __doc__, __file__, parents=[argparser])
  ad_client_id = flags.ad_client_id
  account_id = flags.account_id

  try:
    # Retrieve report.
    result = service.accounts().reports().generate(
        accountId=account_id,
        startDate='2011-01-01',
        endDate='2011-08-31',
        filter=['AD_CLIENT_ID==' + ad_client_id],
        metric=['PAGE_VIEWS', 'AD_REQUESTS', 'AD_REQUESTS_COVERAGE',
                'CLICKS', 'AD_REQUESTS_CTR', 'COST_PER_CLICK',
                'AD_REQUESTS_RPM', 'EARNINGS'],
        dimension=['DATE'],
        sort=['+DATE']).execute()

    if 'rows' in result:
      # Display headers.
      for header in result['headers']:
        print '%25s' % header['name'],
      print
      # Display results.
      for row in result['rows']:
        for column in row:
          print '%25s' % column,
        print
    else:
      print 'No rows returned.'

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
