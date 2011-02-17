#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Simple command-line example for Google URL Shortener API.

Command-line application that shortens a URL.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import httplib2
import pprint

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import AccessTokenCredentials
from oauth2client.tools import run

# Uncomment to get detailed logging
#httplib2.debuglevel = 4


def main():
  storage = Storage('urlshortener.dat')
  credentials = storage.get()

  if credentials is None or credentials.invalid == True:
    flow = OAuth2WebServerFlow(
        client_id='433807057907.apps.googleusercontent.com',
        client_secret='jigtZpMApkRxncxikFpR+SFg',
        scope='https://www.googleapis.com/auth/urlshortener',
        user_agent='urlshortener-cmdline-sample/1.0',
        xoauth_displayname='URL Shortener Client Example App')

    credentials = run(flow, storage)


#  # Test AccessTokenCredentials
#  at_credentials = AccessTokenCredentials(
#      credentials.access_token, 'urlshortener-cmdline-sample/1.0')
#  http = httplib2.Http()
#  http = at_credentials.authorize(http)
#
#  # Build the url shortener service
#  service = build("urlshortener", "v1", http=http,
#            developerKey="AIzaSyDRRpR3GS1F1_jKNNM9HCNd2wJQyPG3oN0")
#  url = service.url()
#
#  # Create a shortened URL by inserting the URL into the url collection.
#  body = {"longUrl": "http://code.google.com/apis/urlshortener/" }
#  resp = url.insert(body=body).execute()
#  pprint.pprint(resp)
#  http = httplib2.Http()
#  http = credentials.authorize(http)
#

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
  main()
