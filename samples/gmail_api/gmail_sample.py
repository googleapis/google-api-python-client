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

"""Simple command-line sample for the Gmail API.
Command-line application that retrieves the snippet of the user's latest 10 emails."""

import sys

from oauth2client import client
from googleapiclient import sample_tools


def main(argv):
    # Authenticate and construct service.
    service, flags = sample_tools.init(
        argv, 'gmail', 'v1', __doc__, __file__,
        scope='https://www.googleapis.com/auth/gmail.readonly')

    try:
        email_list = service.users().messages().list(userId='me', maxResults=10).execute()
        for counter, email in enumerate(email_list.get('messages')):
            message = service.users().messages().get(userId='me', id=email.get('id')).execute()
            print('{} - {}'.format(counter+1, message.get('snippet')))

    except client.AccessTokenRefreshError:
        print('The credentials have been revoked or expired, please re-run'
              'the application to re-authorize.')

if __name__ == '__main__':
    main(sys.argv)
