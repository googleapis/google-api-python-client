#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Simple command-line example for Google URL Shortener API.

Command-line application that shortens a URL.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import gflags
import httplib2
import logging
import pprint
import sys

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

FLAGS = gflags.FLAGS
FLOW = OAuth2WebServerFlow(
    client_id='433807057907.apps.googleusercontent.com',
    client_secret='jigtZpMApkRxncxikFpR+SFg',
    scope='https://www.googleapis.com/auth/urlshortener',
    user_agent='urlshortener-cmdline-sample/1.0')

gflags.DEFINE_enum('logging_level', 'ERROR',
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    'Set the level of logging detail.')


def main(argv):
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError, e:
    print '%s\\nUsage: %s ARGS\\n%s' % (e, argv[0], FLAGS)
    sys.exit(1)

  logging.getLogger().setLevel(getattr(logging, FLAGS.logging_level))

  storage = Storage('urlshortener.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid == True:
    credentials = run(FLOW, storage)

  http = httplib2.Http()
  http = credentials.authorize(http)

  # Build the url shortener service
  service = build("urlshortener", "v1", http=http,
            developerKey="AIzaSyDRRpR3GS1F1_jKNNM9HCNd2wJQyPG3oN0")
  url = service.url()

  # Create a shortened URL by inserting the URL into the url collection.
  body = {"longUrl": "http://code.google.com/apis/urlshortener/" }
  resp = url.insert(body=body).execute()
  pprint.pprint(resp)

  shortUrl = resp['id']

  # Convert the shortened URL back into a long URL
  resp = url.get(shortUrl=shortUrl).execute()
  pprint.pprint(resp)


if __name__ == '__main__':
  main(sys.argv)
