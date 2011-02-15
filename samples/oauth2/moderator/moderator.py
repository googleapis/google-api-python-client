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

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

# Uncomment to get low level HTTP logging
#httplib2.debuglevel = 4


def main():
  storage = Storage('moderator.dat')
  credentials = storage.get()

  if not credentials:
    flow = OAuth2WebServerFlow(
        client_id='433807057907.apps.googleusercontent.com',
        client_secret='jigtZpMApkRxncxikFpR+SFg',
        scope='https://www.googleapis.com/auth/moderator',
        user_agent='moderator-cmdline-sample/1.0',
        xoauth_displayname='Moderator Client Example App')

    credentials = run(flow, storage)

  http = httplib2.Http()
  http = credentials.authorize(http)

  p = build("moderator", "v1", http=http)

  series_body = {
      "data": {
        "description": "Share and rank tips for eating healthy and cheap!",
        "name": "Eating Healthy & Cheap",
        "videoSubmissionAllowed": False
        }
      }
  series = p.series().insert(body=series_body).execute()
  print "Created a new series"

  topic_body = {
      "data": {
        "description": "Share your ideas on eating healthy!",
        "name": "Ideas",
        "presenter": "liz"
        }
      }
  topic = p.topics().insert(seriesId=series['id']['seriesId'],
                            body=topic_body).execute()
  print "Created a new topic"

  submission_body = {
      "data": {
        "attachmentUrl": "http://www.youtube.com/watch?v=1a1wyc5Xxpg",
        "attribution": {
          "displayName": "Bashan",
          "location": "Bainbridge Island, WA"
          },
        "text": "Charlie Ayers @ Google"
        }
      }
  submission = p.submissions().insert(seriesId=topic['id']['seriesId'],
      topicId=topic['id']['topicId'], body=submission_body).execute()
  print "Inserted a new submisson on the topic"

  vote_body = {
      "data": {
        "vote": "PLUS"
        }
      }
  p.votes().insert(seriesId=topic['id']['seriesId'],
                   submissionId=submission['id']['submissionId'],
                   body=vote_body)
  print "Voted on the submission"


if __name__ == '__main__':
  main()
