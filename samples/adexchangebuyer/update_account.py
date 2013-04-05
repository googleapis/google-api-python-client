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

"""This example illustrates how to do a sparse update of the account attributes.

Tags: accounts.patch
"""

__author__ = 'david.t@google.com (David Torres)'

import argparse
import pprint
import sys

from apiclient import sample_tools
from oauth2client import client

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('account_id', type=int,
                     help='The ID of the account to which submit the creative')
argparser.add_argument('cookie_matching_url',
                     help='New cookie matching URL to set for the account ')


def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'adexchangebuyer', 'v1.2', __doc__, __file__, parents=[argparser],
      scope='https://www.googleapis.com/auth/adexchange.buyer')

  account_id = flags.account_id
  cookie_matching_url = flags.cookie_matching_url

  try:
    # Account information to be updated.
    account_body = {
        'accountId': account_id,
        'cookieMatchingUrl': cookie_matching_url
        }
    account = service.accounts().patch(id=account_id,
                                       body=account_body).execute()
    pprint.pprint(account)
  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
