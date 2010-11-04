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
import pprint

# Uncomment the next line to get very detailed logging
# httplib2.debuglevel = 4

def main():

  p = build("diacritize", "v1", developerKey="AIzaSyDRRpR3GS1F1_jKNNM9HCNd2wJQyPG3oN0")
  print p.diacritize().corpus().get(
      lang='ar',
      last_letter='false',
      message=u'مثال لتشكيل'
      ).execute()['diacritized_text']

if __name__ == '__main__':
  main()
