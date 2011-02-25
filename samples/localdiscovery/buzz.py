#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Simple command-line example for Buzz.

Command-line application that retrieves the users
latest content and then adds a new entry.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

from apiclient.discovery import build
from apiclient.discovery import build_from_document
from apiclient.oauth import FlowThreeLegged
from apiclient.ext.authtools import run
from apiclient.ext.file import Storage
from apiclient.oauth import CredentialsInvalidError

import httplib2
import pprint

# Uncomment the next line to get very detailed logging
#httplib2.debuglevel = 4


def main():
  storage = Storage('buzz.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid == True:
    buzz_discovery = build("buzz", "v1").auth_discovery()

    flow = FlowThreeLegged(buzz_discovery,
                           consumer_key='anonymous',
                           consumer_secret='anonymous',
                           user_agent='python-buzz-sample/1.0',
                           domain='anonymous',
                           scope='https://www.googleapis.com/auth/buzz',
                           xoauth_displayname='Google API Client Example App')

    credentials = run(flow, storage)

  http = httplib2.Http()
  http = credentials.authorize(http)

  # Load the local copy of the discovery document
  f = file("buzz.json", "r")
  discovery = f.read()
  f.close()

  # Optionally load a futures discovery document
  f = file("../../apiclient/contrib/buzz/future.json", "r")
  future = f.read()
  f.close()

  # Construct a service from the local documents
  service = build_from_document(discovery,
      base="https://www.googleapis.com/",
      future=future,
      http=http,
      developerKey="AIzaSyDRRpR3GS1F1_jKNNM9HCNd2wJQyPG3oN0")
  activities = service.activities()

  try:
    # Retrieve the first two activities
    activitylist = activities.list(
        max_results='2', scope='@self', userId='@me').execute()
    print "Retrieved the first two activities"
  except CredentialsInvalidError:
    print 'Your credentials are no longer valid.'
    print 'Please re-run this application to re-authorize.'


if __name__ == '__main__':
  main()
