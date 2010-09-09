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

import httplib2
import pickle


def main():
  f = open("moderator.dat", "r")
  credentials = pickle.loads(f.read())
  f.close()

  http = httplib2.Http()
  http = credentials.authorize(http)

  p = build("moderator", "v1", http=http)
  print p.submissions().list(seriesId="7035", topicId="64")

if __name__ == '__main__':
  main()
