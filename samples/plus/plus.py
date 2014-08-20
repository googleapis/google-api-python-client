#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Google Inc. All Rights Reserved.
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

"""Simple command-line sample for the Google+ API.

Command-line application that retrieves the list of the user's posts."""
from __future__ import print_function

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import sys

from oauth2client import client
from googleapiclient import sample_tools


def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'plus', 'v1', __doc__, __file__,
      scope='https://www.googleapis.com/auth/plus.me')

  try:
    person = service.people().get(userId='me').execute()

    print('Got your ID: %s' % person['displayName'])
    print()
    print('%-040s -> %s' % ('[Activitity ID]', '[Content]'))

    # Don't execute the request until we reach the paging loop below.
    request = service.activities().list(
        userId=person['id'], collection='public')

    # Loop over every activity and print the ID and a short snippet of content.
    while request is not None:
      activities_doc = request.execute()
      for item in activities_doc.get('items', []):
        print('%-040s -> %s' % (item['id'], item['object']['content'][:30]))

      request = service.activities().list_next(request, activities_doc)

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run'
      'the application to re-authorize.')

if __name__ == '__main__':
  main(sys.argv)
