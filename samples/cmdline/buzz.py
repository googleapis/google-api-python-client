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
  f = open("oauth_token.dat", "r")
  credentials = pickle.loads(f.read())
  f.close()

  http = httplib2.Http()
  http = credentials.authorize(http)

  p = build("buzz", "v1", http=http)
  activities = p.activities()
  activitylist = activities.list(scope='@self', userId='@me')
  print activitylist['items'][0]['title']
  activities.insert(userId='@me', body={
    'title': 'Testing insert',
    'object': {
      'content': u'Just a short note to show that insert is working. ☄',
      'type': 'note'}
    }
  )

if __name__ == '__main__':
  main()
