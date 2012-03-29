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

"""This example gets all accounts for the logged in user.

Tags: accounts.list
"""

__author__ = 'david.t@google.com (David Torres)'

import pprint
import sys
from oauth2client.client import AccessTokenRefreshError
import sample_utils


def main(argv):
  sample_utils.process_flags(argv)
  pretty_printer = pprint.PrettyPrinter()

  # Authenticate and construct service
  service = sample_utils.initialize_service()

  try:
    # Retrieve account list and display data as received
    result = service.accounts().list().execute()
    pretty_printer.pprint(result)
  except AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
