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

import pprint
import sys
import gflags
from oauth2client.client import AccessTokenRefreshError
import sample_utils

# Declare command-line flags, and set them as required.
gflags.DEFINE_string('account_id', None,
                     'The ID of the account to which submit the creative',
                     short_name='a')
gflags.MarkFlagAsRequired('account_id')
gflags.DEFINE_string('cookie_matching_url', None,
                     'New cookie matching URL to set for the account ',
                     short_name='u')
gflags.MarkFlagAsRequired('cookie_matching_url')


def main(argv):
  sample_utils.process_flags(argv)
  account_id = gflags.FLAGS.account_id
  cookie_matching_url = gflags.FLAGS.cookie_matching_url
  pretty_printer = pprint.PrettyPrinter()

  # Authenticate and construct service.
  service = sample_utils.initialize_service()

  try:
    # Account information to be updated.
    account_body = {
        'accountId': account_id,
        'cookieMatchingUrl': cookie_matching_url
        }
    account = service.accounts().patch(id=account_id,
                                       body=account_body).execute()
    pretty_printer.pprint(account)
  except AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
