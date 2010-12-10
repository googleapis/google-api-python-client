#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Simple command-line example for Custom Search.

Command-line application that does a search.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

from apiclient.discovery import build

import pprint

# Uncomment the next line to get very detailed logging
# httplib2.debuglevel = 4


def main():
  p = build("customsearch", "v1",
            developerKey="AIzaSyDRRpR3GS1F1_jKNNM9HCNd2wJQyPG3oN0")
  res = p.cse().list(
      q='lectures',
      cx='017576662512468239146:omuauf_lfve',
    ).execute()
  pprint.pprint(res)

if __name__ == '__main__':
  main()
