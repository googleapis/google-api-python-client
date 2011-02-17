#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Simple command-line example for Buzz.

Command-line application that retrieves the users
latest content and then adds a new entry.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import httplib2
import pickle
import pprint

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

# Uncomment the next line to get very detailed logging
#httplib2.debuglevel = 4


def main():
  storage = Storage('buzz.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid == True:
    flow = OAuth2WebServerFlow(
        client_id='433807057907.apps.googleusercontent.com',
        client_secret='jigtZpMApkRxncxikFpR+SFg',
        scope='https://www.googleapis.com/auth/buzz',
        user_agent='buzz-cmdline-sample/1.0',
        domain='anonymous',
        xoauth_displayname='Buzz Client Example App'
        )
    credentials = run(flow, storage)

  http = httplib2.Http()
  http = credentials.authorize(http)

  p = build("buzz", "v1", http=http,
            developerKey="AIzaSyDRRpR3GS1F1_jKNNM9HCNd2wJQyPG3oN0")
  activities = p.activities()

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
  activity = activities.insert(userId='@me', body=new_activity_body).execute()
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

if __name__ == '__main__':
  main()
