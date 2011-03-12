#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Simple command-line example for Buzz.

Command-line application that retrieves the users
latest content and then adds a new entry.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import gflags
import httplib2
import logging
import pprint
import sys

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

FLAGS = gflags.FLAGS
FLOW = OAuth2WebServerFlow(
    client_id='433807057907.apps.googleusercontent.com',
    client_secret='jigtZpMApkRxncxikFpR+SFg',
    scope='https://www.googleapis.com/auth/buzz',
    user_agent='buzz-cmdline-sample/1.0')

gflags.DEFINE_enum('logging_level', 'ERROR',
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    'Set the level of logging detail.')


def main(argv):
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError, e:
    print '%s\\nUsage: %s ARGS\\n%s' % (e, argv[0], FLAGS)
    sys.exit(1)

  logging.getLogger().setLevel(getattr(logging, FLAGS.logging_level))

  storage = Storage('buzz.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid == True:
    credentials = run(FLOW, storage)

  http = httplib2.Http()
  http = credentials.authorize(http)

  # Build the Buzz service
  service = build("buzz", "v1", http=http,
            developerKey="AIzaSyDRRpR3GS1F1_jKNNM9HCNd2wJQyPG3oN0")
  activities = service.activities()

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
      'title': 'Testing insert',
      'object': {
        'content':
        u'Just a short note to show that insert is working. ☄',
        'type': 'note'}
      }
  activity = activities.insert(userId='@me', body=new_activity_body).execute()
  print "Added a new activity"

  activitylist = activities.list(
      max_results='2', scope='@self', userId='@me').execute()

  # Add a comment to that activity
  comment_body = {
      "content": "This is a comment"
      }
  item = activitylist['items'][0]
  comment = service.comments().insert(
      userId=item['actor']['id'], postId=item['id'], body=comment_body
      ).execute()
  print 'Added a comment to the new activity'
  pprint.pprint(comment)

if __name__ == '__main__':
  main(sys.argv)
