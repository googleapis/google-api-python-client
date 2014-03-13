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

"""This example adds a new ad unit to a publisher ad client.

To get ad clients, run get_all_ad_clients_for_publisher.py.

Tags: accounts.adunits.insert
"""

__author__ = 'jalc@google.com (Jose Alcerreca)'

import argparse
import sys

from apiclient import sample_tools
from oauth2client import client
from sample_utils import GetUniqueName

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument(
    'account_id',
    help='The ID of the pub account on which to create the ad unit')
argparser.add_argument(
    'ad_client_id',
    help='The ID of the ad client on which to create the ad unit')


def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'adsensehost', 'v4.1', __doc__, __file__, parents=[argparser])
  account_id = flags.account_id
  ad_client_id = flags.ad_client_id

  try:
    ad_unit = {
        'name': 'Ad Unit #%s' % GetUniqueName(),
        'contentAdsSettings': {
            'backupOption': {
                'type': 'COLOR',
                'color': 'ffffff'
            },
            'size': 'SIZE_200_200',
            'type': 'TEXT'
        },
        'customStyle': {
            'colors': {
                'background': 'ffffff',
                'border': '000000',
                'text': '000000',
                'title': '000000',
                'url': '0000ff'
            },
            'corners': 'SQUARE',
            'font': {
                'family': 'ACCOUNT_DEFAULT_FAMILY',
                'size': 'ACCOUNT_DEFAULT_SIZE'
            }
        }
    }

    # Create ad unit.
    request = service.accounts().adunits().insert(adClientId=ad_client_id,
                                                  accountId=account_id,
                                                  body=ad_unit)

    result = request.execute()
    print ('Ad unit of type "%s", name "%s" and status "%s" was created.' %
           (result['contentAdsSettings']['type'], result['name'],
            result['status']))

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
