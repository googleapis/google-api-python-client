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

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

def main(argv):
  # Load the json format key that you downloaded from the Google API
  # Console when you created your service account. For p12 keys, use the
  # from_p12_keyfile method of ServiceAccountCredentials and specify the 
  # service account email address, p12 keyfile, and scopes.
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      'service-account-abcdef123456.json',
      scopes='https://www.googleapis.com/auth/tasks')

  # Create an httplib2.Http object to handle our HTTP requests and authorize
  # it with the Credentials.
  http = httplib2.Http()
  http = credentials.authorize(http)

  service = build("tasks", "v1", http=http)

  # List all the tasklists for the account.
  lists = service.tasklists().list().execute(http=http)
  pprint.pprint(lists)


if __name__ == '__main__':
  main(sys.argv)
