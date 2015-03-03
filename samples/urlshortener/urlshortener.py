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

"""Command-line sample for the Google URL Shortener API.

Simple command-line example for Google URL Shortener API that shortens
a URI then expands it.

Usage:
  $ python urlshortener.py

You can also get help on all the command-line flags the program understands
by running:

  $ python urlshortener.py --help

To get detailed log output run:

  $ python urlshortener.py --logging_level=DEBUG
"""
from __future__ import print_function

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import pprint
import sys

from oauth2client import client
from googleapiclient import sample_tools

def main(argv):
  service, flags = sample_tools.init(
      argv, 'urlshortener', 'v1', __doc__, __file__,
      scope='https://www.googleapis.com/auth/urlshortener')

  try:
    url = service.url()

    # Create a shortened URL by inserting the URL into the url collection.
    body = {'longUrl': 'http://code.google.com/apis/urlshortener/' }
    resp = url.insert(body=body).execute()
    pprint.pprint(resp)

    short_url = resp['id']

    # Convert the shortened URL back into a long URL
    resp = url.get(shortUrl=short_url).execute()
    pprint.pprint(resp)

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run'
      'the application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
