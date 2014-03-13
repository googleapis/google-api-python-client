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

"""This example adds a URL channel to a host ad client.

To get ad clients, run get_all_ad_clients_for_host.py.

Tags: urlchannels.insert
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
    help='The ID of the ad client on which to create the URL channel')
argparser.add_argument(
    'url_pattern',
    help='The URL pattern for the new custom channel')


def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'adsensehost', 'v4.1', __doc__, __file__, parents=[argparser])
  ad_client_id = flags.ad_client_id
  url_pattern = flags.url_pattern

  try:
    custom_channel = {
        'urlPattern': url_pattern
    }

    # Add URL channel.
    request = service.urlchannels().insert(adClientId=ad_client_id,
                                           body=custom_channel)

    result = request.execute()
    print ('URL channel with id "%s" and URL pattern "%s" was created.' %
           (result['id'], result['urlPattern']))

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
