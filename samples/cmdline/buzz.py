#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Simple command-line example for Buzz.

Command-line application that retrieves the users
latest content and then adds a new entry.
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

def main():
  f = open("buzz.dat", "r")
  credentials = pickle.loads(f.read())
  f.close()

  http = httplib2.Http()
  http = credentials.authorize(http)

  p = build("buzz", "v1", http=http)
  activities = p.activities()
  activitylist = activities.list(max_results='2', scope='@self', userId='@me').execute()
  print activitylist['items'][0]['title']
  activitylist = activities.list_next(activitylist).execute()
  print activitylist['items'][0]['title']

  activity = activities.insert(userId='@me', body={
    'title': 'Testing insert',
    'object': {
      'content': u'Just a short note to show that insert is working. ☄',
      'type': 'note'}
    }
  ).execute()
  pprint.pprint(activity)
  print
  print 'Just created: ', activity['links']['alternate'][0]['href']

if __name__ == '__main__':
  main()
