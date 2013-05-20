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

"""This example gets all accounts for the logged in user.

Tags: accounts.list
"""

__author__ = 'sergio.gomes@google.com (Sergio Gomes)'

import sys

from apiclient import sample_tools
from oauth2client import client

MAX_PAGE_SIZE = 50


def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'adsense', 'v1.2', __doc__, __file__, parents=[],
      scope='https://www.googleapis.com/auth/adsense.readonly')

  try:
    # Retrieve account list in pages and display data as we receive it.
    request = service.accounts().list(maxResults=MAX_PAGE_SIZE)

    while request is not None:
      result = request.execute()
      accounts = result['items']
      for account in accounts:
        print ('Account with ID "%s" and name "%s" was found. '
               % (account['id'], account['name']))

      request = service.accounts().list_next(request, result)

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
