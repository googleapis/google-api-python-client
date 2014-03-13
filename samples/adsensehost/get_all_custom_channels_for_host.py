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

"""This example gets all custom channels in a host ad client.

To get ad clients, run get_all_ad_clients_for_host.py.

Tags: customchannels.list
"""

__author__ = 'jalc@google.com (Jose Alcerreca)'

import argparse
import sys

from apiclient import sample_tools
from oauth2client import client

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument(
    'ad_client_id',
    help='The ad client ID for which to get custom channels')


MAX_PAGE_SIZE = 50


def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'adsensehost', 'v4.1', __doc__, __file__, parents=[argparser])
  ad_client_id = flags.ad_client_id

  try:
    # Retrieve custom channel list in pages and display data as we receive it.
    request = service.customchannels().list(adClientId=ad_client_id,
                                            maxResults=MAX_PAGE_SIZE)

    while request is not None:
      result = request.execute()
      if 'items' in result:
        custom_channels = result['items']
        for custom_channel in custom_channels:
          print ('Custom channel with ID "%s", code "%s" and name "%s" found.'
                 % (custom_channel['id'], custom_channel['code'],
                    custom_channel['name']))

        request = service.customchannels().list_next(request, result)
      else:
        print 'No custom channels were found.'
        break

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
