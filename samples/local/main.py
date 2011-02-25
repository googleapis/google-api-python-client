#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Simple command-line example for running against a
  local server.

"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

# Enable this sample to be run from the top-level directory
import os
import sys
sys.path.insert(0, os.getcwd())

from apiclient.discovery import build

import httplib2
# httplib2.debuglevel = 4
import pickle
import pprint

DISCOVERY_URI = ('http://localhost:3990/discovery/v0.2beta1/describe/'
  '{api}/{apiVersion}')


def main():
  http = httplib2.Http()

  service = build("buzz", "v1", http=http, discoveryServiceUrl=DISCOVERY_URI)
  help(service.activities().list)
  print service.activities().list(userId='@self', scope='@me', c='foo').uri

if __name__ == '__main__':
  main()
