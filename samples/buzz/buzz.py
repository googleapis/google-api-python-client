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
from apiclient.oauth import FlowThreeLegged
from apiclient.ext.authtools import run
from apiclient.ext.file import Storage
from apiclient.oauth import CredentialsInvalidError

import httplib2
import pickle
import pprint

# Uncomment the next line to get very detailed logging
#httplib2.debuglevel = 4


def main():
  credentials = Storage('buzz.dat').get()
  if credentials is None or credentials.invalid == True:
    buzz_discovery = build("buzz", "v1").auth_discovery()

    flow = FlowThreeLegged(buzz_discovery,
                           consumer_key='anonymous',
                           consumer_secret='anonymous',
                           user_agent='python-buzz-sample/1.0',
                           domain='anonymous',
                           scope='https://www.googleapis.com/auth/buzz',
                           xoauth_displayname='Google API Client Example App')

    credentials = run(flow, 'buzz.dat')

  http = httplib2.Http()
  http = credentials.authorize(http)

  p = build("buzz", "v1", http=http,
      developerKey="AIzaSyDRRpR3GS1F1_jKNNM9HCNd2wJQyPG3oN0")
  activities = p.activities()

  try:
    # Retrieve the first two activities
    activitylist = activities.list(
        max_results='2', scope='@self', userId='@me').execute()
    print "Retrieved the first two activities"

    # Retrieve the next two activities
    if activitylist:
      activitylist = activities.list_next(activitylist).execute()
      print "Retrieved the next two activities"

    # Add a new activity
    new_activity_body = {
        "data": {
          'title': 'Testing insert',
          'object': {
            'content':
              u'Just a short note to show that insert is working. ☄',
            'type': 'note'}
          }
        }
    activity = activities.insert(
        userId='@me', body=new_activity_body).execute()
    print "Added a new activity"

    activitylist = activities.list(
        max_results='2', scope='@self', userId='@me').execute()

    # Add a comment to that activity
    comment_body = {
        "data": {
            "content": "This is a comment"
            }
        }
    item = activitylist['items'][0]
    comment = p.comments().insert(
        userId=item['actor']['id'], postId=item['id'], body=comment_body
        ).execute()
    print 'Added a comment to the new activity'
    pprint.pprint(comment)
  except CredentialsInvalidError:
    print 'Your credentials are no longer valid.'
    print 'Please re-run this application to re-authorize.'

if __name__ == '__main__':
  main()
