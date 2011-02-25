#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Simple command-line example for Latitude.

Command-line application that sets the users
current location.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import httplib2

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run
from apiclient.oauth import CredentialsInvalidError

# Uncomment to get detailed logging
#httplib2.debuglevel = 4


def main():
  credentials = Storage('latitude.dat').get()
  if credentials is None or credentials.invalid:
    flow = OAuth2WebServerFlow(
        client_id='433807057907.apps.googleusercontent.com',
        client_secret='jigtZpMApkRxncxikFpR+SFg',
        scope='https://www.googleapis.com/auth/latitude',
        user_agent='latitude-cmdline-sample/1.0',
        xoauth_displayname='Latitude Client Example App')

    credentials = run(flow, storage)

  http = httplib2.Http()
  http = credentials.authorize(http)

  service = build("latitude", "v1", http=http)

  body = {
      "data": {
          "kind": "latitude#location",
          "latitude": 37.420352,
          "longitude": -122.083389,
          "accuracy": 130,
          "altitude": 35
          }
      }
  try:
    print service.currentLocation().insert(body=body).execute()
  except CredentialsInvalidError:
    print 'Your credentials are no longer valid.'
    print 'Please re-run this application to re-authorize.'

if __name__ == '__main__':
  main()
