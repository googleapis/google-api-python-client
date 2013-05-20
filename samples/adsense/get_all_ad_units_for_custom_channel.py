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

"""This example gets all ad units corresponding to a specified custom channel.

To get custom channels, run get_all_custom_channels.py.

Tags: accounts.customchannels.adunits.list
"""

__author__ = 'sergio.gomes@google.com (Sergio Gomes)'

import argparse
import sys

from apiclient import sample_tools
from oauth2client import client

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('account_id',
    help='The ID of the account with the specified custom channel')
argparser.add_argument('ad_client_id',
    help='The ID of the ad client for which to generate a report')
argparser.add_argument('custom_channel_id',
    help='The ID of the custom channel for which to get ad units')

MAX_PAGE_SIZE = 50


def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'adsense', 'v1.2', __doc__, __file__, parents=[argparser],
      scope='https://www.googleapis.com/auth/adsense.readonly')

  # Process flags and read their values.
  account_id = flags.account_id
  ad_client_id = flags.ad_client_id
  custom_channel_id = flags.custom_channel_id

  try:
    # Retrieve ad unit list in pages and display data as we receive it.
    request = service.accounts().customchannels().adunits().list(
        accountId=account_id, adClientId=ad_client_id,
        customChannelId=custom_channel_id, maxResults=MAX_PAGE_SIZE)

    while request is not None:
      result = request.execute()
      ad_units = result['items']
      for ad_unit in ad_units:
        print ('Ad unit with code "%s", name "%s" and status "%s" was found. ' %
               (ad_unit['code'], ad_unit['name'], ad_unit['status']))

      request = service.adunits().list_next(request, result)

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
