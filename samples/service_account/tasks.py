#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Google Inc.
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

"""Simple command-line sample that demonstrates service accounts.

Lists all the Google Task Lists associated with the given service account.
Service accounts are created in the Google API Console. See the documentation
for more information:

   https://developers.google.com/console/help/#WhatIsKey

Usage:
  $ python tasks.py
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import httplib2
import pprint
import sys

from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials

def main(argv):
  # Load the key in PKCS 12 format that you downloaded from the Google API
  # Console when you created your Service account.
  f = file('key.p12', 'rb')
  key = f.read()
  f.close()

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with the Credentials. Note that the first parameter, service_account_name,
  # is the Email address created for the Service account. It must be the email
  # address associated with the key that was created.
  credentials = SignedJwtAssertionCredentials(
      '141491975384@developer.gserviceaccount.com',
      key,
      scope='https://www.googleapis.com/auth/tasks')
  http = httplib2.Http()
  http = credentials.authorize(http)

  service = build("tasks", "v1", http=http)

  # List all the tasklists for the account.
  lists = service.tasklists().list().execute(http=http)
  pprint.pprint(lists)


if __name__ == '__main__':
  main(sys.argv)
