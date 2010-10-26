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

# Uncomment to get detailed logging
# httplib2.debuglevel = 4

def main():
  f = open("latitude.dat", "r")
  credentials = pickle.loads(f.read())
  f.close()

  http = httplib2.Http()
  http = credentials.authorize(http)

  p = build("latitude", "v1", http=http)

  body = {
      "data": {
          "kind":"latitude#location",
          "latitude":37.420352,
          "longitude":-122.083389,
          "accuracy":130,
          "altitude":35
          }
      }
  print p.currentLocation().insert(body=body).execute()

if __name__ == '__main__':
  main()
