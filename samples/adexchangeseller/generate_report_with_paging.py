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

"""This example retrieves a report for the specified ad client.

Please only use pagination if your application requires it due to memory or
storage constraints.
If you need to retrieve more than 5000 rows, please check generate_report.py, as
due to current limitations you will not be able to use paging for large reports.
To get ad clients, run get_all_ad_clients.py.

Tags: reports.generate
"""
from __future__ import print_function

__author__ = 'sgomes@google.com (Sérgio Gomes)'

import argparse
import sys

from googleapiclient import sample_tools
from oauth2client import client

MAX_PAGE_SIZE = 50
# This is the maximum number of obtainable rows for paged reports.
ROW_LIMIT = 5000

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('ad_client_id',
    help='The ID of the ad client for which to generate a report')


def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'adexchangeseller', 'v1.1', __doc__, __file__, parents=[argparser],
      scope='https://www.googleapis.com/auth/adexchange.seller.readonly')

  ad_client_id = flags.ad_client_id

  try:
    # Retrieve report in pages and display data as we receive it.
    start_index = 0
    rows_to_obtain = MAX_PAGE_SIZE
    while True:
      result = service.reports().generate(
          startDate='2011-01-01', endDate='2011-08-31',
          filter=['AD_CLIENT_ID==' + ad_client_id],
          metric=['PAGE_VIEWS', 'AD_REQUESTS', 'AD_REQUESTS_COVERAGE',
                  'CLICKS', 'AD_REQUESTS_CTR', 'COST_PER_CLICK',
                  'AD_REQUESTS_RPM', 'EARNINGS'],
          dimension=['DATE'],
          sort=['+DATE'],
          startIndex=start_index,
          maxResults=rows_to_obtain).execute()

      # If this is the first page, display the headers.
      if start_index == 0:
        for header in result['headers']:
          print('%25s' % header['name'], end=' ')
        print()

      # Display results for this page.
      for row in result['rows']:
        for column in row:
          print('%25s' % column, end=' ')
        print()

      start_index += len(result['rows'])

      # Check to see if we're going to go above the limit and get as many
      # results as we can.
      if start_index + MAX_PAGE_SIZE > ROW_LIMIT:
        rows_to_obtain = ROW_LIMIT - start_index
        if rows_to_obtain <= 0:
          break

      if (start_index >= int(result['totalMatchedRows'])):
        break

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
