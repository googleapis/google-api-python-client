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

"""This example updates a custom channel on a host ad client.

To get ad clients, run get_all_ad_clients_for_host.py.
To get custom channels, run get_all_custom_channels_for_host.py.

Tags: customchannels.patch
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
    'ad_client_id',
    help='The ad client ID that contains the custom channel')
argparser.add_argument(
    'custom_channel_id',
    help='The ID of the custom channel to be updated')


def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'adsensehost', 'v4.1', __doc__, __file__, parents=[argparser])
  ad_client_id = flags.ad_client_id
  custom_channel_id = flags.custom_channel_id

  try:
    custom_channel = {
        'name': 'Updated Sample Channel #%s' % GetUniqueName()
    }

    # Update custom channel.
    request = service.customchannels().patch(adClientId=ad_client_id,
                                             customChannelId=custom_channel_id,
                                             body=custom_channel)

    result = request.execute()
    print ('Custom channel with ID "%s" was updated with name "%s".'
           % (result['id'], result['name']))

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
