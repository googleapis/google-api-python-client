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

# Uncomment to get detailed logging
# httplib2.debuglevel = 4

def main():
  f = open("moderator.dat", "r")
  credentials = pickle.loads(f.read())
  f.close()

  http = httplib2.Http()
  http = credentials.authorize(http)

  p = build("moderator", "v1", http=http)

  series_body = {
      "data": {
        "description": "Share and rank tips for eating healthily on the cheaps!",
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
  topic = p.topics().insert(seriesId=series['id']['seriesId'], body=topic_body).execute()
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
  p.votes().insert(seriesId=topic['id']['seriesId'], submissionId=submission['id']['submissionId'], body=vote_body)
  print "Voted on the submission"


if __name__ == '__main__':
  main()
