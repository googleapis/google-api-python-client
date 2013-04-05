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

"""This example illustrates how to retrieve the information of a creative.

Tags: creatives.insert
"""

__author__ = ('david.t@google.com (David Torres)',
              'jdilallo@google.com (Joseph DiLallo)')

import argparse
import pprint
import sys

from apiclient import sample_tools
from oauth2client import client

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('account_id', type=int,
                     help='The ID of the account that contains the creative')
argparser.add_argument('buyer_creative_id',
                     help='A buyer-specific id that identifies this creative')


def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'adexchangebuyer', 'v1.2', __doc__, __file__, parents=[argparser],
      scope='https://www.googleapis.com/auth/adexchange.buyer')

  account_id = flags.account_id
  buyer_creative_id = flags.buyer_creative_id

  try:
    # Construct the request.
    request = service.creatives().get(accountId=account_id,
                                      buyerCreativeId=buyer_creative_id)

    # Execute request and print response.
    pprint.pprint(request.execute())
  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
