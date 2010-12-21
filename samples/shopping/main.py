#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Simple command-line example for The Google Shopping API.

Command-line application that does a search for products.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

from apiclient.discovery import build

import pprint

# Uncomment the next line to get very detailed logging
# httplib2.debuglevel = 4


def main():
  p = build("shopping", "v1",
            developerKey="AIzaSyDRRpR3GS1F1_jKNNM9HCNd2wJQyPG3oN0")
  res = p.products().list(
      country='US',
      source='public',
      q='logitech revue'
      ).execute()
  pprint.pprint(res)

if __name__ == '__main__':
  main()
