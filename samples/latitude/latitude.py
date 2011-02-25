#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Simple command-line example for Latitude.

Command-line application that sets the users
current location.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'


from apiclient.discovery import build

import httplib2
import pickle

from apiclient.discovery import build
from apiclient.oauth import FlowThreeLegged
from apiclient.ext.authtools import run
from apiclient.ext.file import Storage

# Uncomment to get detailed logging
# httplib2.debuglevel = 4


def main():
  storage = Storage('latitude.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid == True:
    auth_discovery = build("latitude", "v1").auth_discovery()
    flow = FlowThreeLegged(auth_discovery,
                           # You MUST have a consumer key and secret tied to a
                           # registered domain to use the latitude API.
                           #
                           # https://www.google.com/accounts/ManageDomains
                           consumer_key='REGISTERED DOMAIN NAME',
                           consumer_secret='KEY GIVEN DURING REGISTRATION',
                           user_agent='google-api-client-python-latitude/1.0',
                           domain='REGISTERED DOMAIN NAME',
                           scope='https://www.googleapis.com/auth/latitude',
                           xoauth_displayname='Google API Latitude Example',
                           location='current',
                           granularity='city'
                           )

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
  print service.currentLocation().insert(body=body).execute()

if __name__ == '__main__':
  main()
