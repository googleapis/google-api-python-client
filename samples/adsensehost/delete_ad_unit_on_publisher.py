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

"""This example deletes an ad unit on a publisher ad client.

To get ad clients, run get_all_ad_clients_for_publisher.py.
To get ad units, run get_all_ad_units_for_publisher.py.

Tags: accounts.adunits.delete
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
    help='The ID of the pub account on which the ad unit exists')
argparser.add_argument(
    'ad_client_id',
    help='The ID of the ad client on which the ad unit exists')
argparser.add_argument(
    'ad_unit_id',
    help='The ID of the ad unit to be deleted')


def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'adsensehost', 'v4.1', __doc__, __file__, parents=[argparser])
  account_id = flags.account_id
  ad_client_id = flags.ad_client_id
  ad_unit_id = flags.ad_unit_id

  try:
    # Delete ad unit.
    request = service.accounts().adunits().delete(accountId=account_id,
                                                  adClientId=ad_client_id,
                                                  adUnitId=ad_unit_id)

    result = request.execute()
    print 'Ad unit with ID "%s" was deleted.' % result['id']

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
