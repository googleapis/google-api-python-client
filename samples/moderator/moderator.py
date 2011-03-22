#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Simple command-line example for Moderator.

Command-line application that exercises the Google Moderator API.

Usage:
  $ python moderator.py

You can also get help on all the command-line flags the program understands
by running:

  $ python moderator.py --help

To get detailed log output run:

  $ python moderator.py --logging_level=DEBUG
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import gflags
import httplib2
import logging
import sys

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

FLAGS = gflags.FLAGS

# Set up a Flow object to be used if we need to authenticate. This
# sample uses OAuth 2.0, and we set up the OAuth2WebServerFlow with
# the information it needs to authenticate. Note that it is called
# the Web Server Flow, but it can also handle the flow for native
# applications <http://code.google.com/apis/accounts/docs/OAuth2.html#IA>
# The client_id client_secret are copied from the Identity tab on
# the Google APIs Console <http://code.google.com/apis/console>
FLOW = OAuth2WebServerFlow(
    client_id='433807057907.apps.googleusercontent.com',
    client_secret='jigtZpMApkRxncxikFpR+SFg',
    scope='https://www.googleapis.com/auth/moderator',
    user_agent='moderator-cmdline-sample/1.0')

# The gflags module makes defining command-line options easy for
# applications. Run this program with the '--help' argument to see
# all the flags that it understands.
gflags.DEFINE_enum('logging_level', 'ERROR',
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    'Set the level of logging detail.')


def main(argv):
  # Let the gflags module process the command-line arguments
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError, e:
    print '%s\\nUsage: %s ARGS\\n%s' % (e, argv[0], FLAGS)
    sys.exit(1)

  # Set the logging according to the command-line flag
  logging.getLogger().setLevel(getattr(logging, FLAGS.logging_level))

  # A Storage object is used to storage and retrieve Credentials.
  # See <http://code.google.com/p/google-api-python-client/wiki/HowAuthenticationWorks>
  storage = Storage('moderator.dat')
  credentials = storage.get()

  # If the Credentials don't exist or are invalid run through the
  # native client flow. The Storage object will ensure that if successful
  # the good Credentials will get written back to a file.
  if credentials is None or credentials.invalid == True:
    credentials = run(FLOW, storage)

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  http = httplib2.Http(cache=".cache")
  http = credentials.authorize(http)

  # Build a service object for interacting with the API.
  service = build("moderator", "v1", http=http)

  # Create a new Moderator series.
  series_body = {
        "description": "Share and rank tips for eating healthy and cheap!",
        "name": "Eating Healthy & Cheap",
        "videoSubmissionAllowed": False
        }
  series = service.series().insert(body=series_body).execute()
  print "Created a new series"

  # Create a new Moderator topic in that series.
  topic_body = {
        "description": "Share your ideas on eating healthy!",
        "name": "Ideas",
        "presenter": "liz"
        }
  topic = service.topics().insert(seriesId=series['id']['seriesId'],
                            body=topic_body).execute()
  print "Created a new topic"

  # Create a new Submission in that topic.
  submission_body = {
        "attachmentUrl": "http://www.youtube.com/watch?v=1a1wyc5Xxpg",
        "attribution": {
          "displayName": "Bashan",
          "location": "Bainbridge Island, WA"
          },
        "text": "Charlie Ayers @ Google"
        }
  submission = service.submissions().insert(seriesId=topic['id']['seriesId'],
      topicId=topic['id']['topicId'], body=submission_body).execute()
  print "Inserted a new submisson on the topic"

  # Vote on that newly added Submission.
  vote_body = {
        "vote": "PLUS"
        }
  service.votes().insert(seriesId=topic['id']['seriesId'],
                   submissionId=submission['id']['submissionId'],
                   body=vote_body)
  print "Voted on the submission"


if __name__ == '__main__':
  main(sys.argv)
