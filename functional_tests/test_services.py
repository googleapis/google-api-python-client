#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Discovery document tests

Functional tests that verify we can retrieve data from existing services.

These tests are read-only in order to ensure they're repeatable. They also
only work with publicly visible data in order to avoid dealing with OAuth.
"""
import httplib2

__author__ = 'ade@google.com (Ade Oshineye)'

from apiclient.discovery import build
import httplib2
import logging
import pickle
import os
import unittest

# TODO(ade) Remove this mock once the bug in the discovery document is fixed
DATA_DIR = os.path.join(logging.os.path.dirname(__file__), '../tests/data')
class HttpMock(object):

  def __init__(self, filename, headers):
    f = file(os.path.join(DATA_DIR, filename), 'r')
    self.data = f.read()
    f.close()
    self.headers = headers

  def request(self, uri, method="GET", body=None, headers=None, redirections=1, connection_type=None):
    return httplib2.Response(self.headers), self.data

class BuzzFunctionalTest(unittest.TestCase):
  def test_can_get_buzz_activities_with_many_params(self):
    buzz = build('buzz', 'v1')
    max_results = 2
    actcol = buzz.activities()
    activities = actcol.list(userId='googlebuzz', scope='@self',
                             max_comments=max_results*2 ,max_liked=max_results*3,
                             max_results=max_results).execute()
    activity_count = len(activities['items'])
    self.assertEquals(max_results, activity_count)

    activities = actcol.list_next(activities).execute()
    activity_count = len(activities['items'])
    self.assertEquals(max_results, activity_count)

  def test_can_get_multiple_pages_of_buzz_activities(self):
    buzz = build('buzz', 'v1')
    max_results = 2
    actcol = buzz.activities()
    
    activities = actcol.list(userId='adewale', scope='@self',
                             max_results=max_results).execute()
    for count in range(10):
      activities = actcol.list_next(activities).execute()
      activity_count = len(activities['items'])
      self.assertEquals(max_results, activity_count, 'Failed after %s pages' % str(count))

  def IGNORE__test_can_get_multiple_pages_of_buzz_likers(self):
    # Ignore this test until the Buzz API fixes the bug with next links
    # http://code.google.com/p/google-buzz-api/issues/detail?id=114
    self.http = HttpMock('buzz.json', {'status': '200'})
    buzz = build('buzz', 'v1', self.http)
    max_results = 1
    people_cmd = buzz.people()
    #https://www.googleapis.com/buzz/v1/activities/111062888259659218284/@self/B:z13nh535yk2syfob004cdjyb3mjeulcwv3c?alt=json#
    people = people_cmd.liked(groupId='@liked', userId='googlebuzz', scope='@self',
                              postId='B:z13nh535yk2syfob004cdjyb3mjeulcwv3c', max_results=max_results).execute()

    for count in range(10):
      people = people_cmd.liked_next(people).execute()
      people_count = len(people['items'])
      self.assertEquals(max_results, people_count, 'Failed after %s pages' % str(count))

  def test_can_get_user_profile(self):
    buzz = build('buzz', 'v1')
    person = buzz.people().get(userId='googlebuzz').execute()

    self.assertTrue(person is not None)
    self.assertEquals('buzz#person', person['kind'])
    self.assertEquals('Google Buzz Team', person['displayName'])
    self.assertEquals('111062888259659218284', person['id'])
    self.assertEquals('http://www.google.com/profiles/googlebuzz', person['profileUrl'])


class BuzzAuthenticatedFunctionalTest(unittest.TestCase):
  def __init__(self, method_name):
    unittest.TestCase.__init__(self, method_name)
    credentials_dir = os.path.join(logging.os.path.dirname(__file__), './data')
    f = file(os.path.join(credentials_dir, 'buzz_credentials.dat'), 'r')
    credentials = pickle.loads(f.read())
    f.close()

    self.http = credentials.authorize(httplib2.Http())

  def test_can_list_groups_belonging_to_user(self):
    # TODO(ade) This should not require authentication. It does because we're adding a spurious @self to the URL
    buzz = build('buzz', 'v1', http=self.http)
    groups = buzz.groups().list(userId='108242092577082601423').execute()

    # This should work as long as no-one edits the groups for this test account
    expected_default_number_of_groups = 4
    self.assertEquals(expected_default_number_of_groups, len(groups['items']))

  def IGNORE__test_can_get_followees_of_user(self):
    # This currently fails with:
    # Attempting to access self view of a different user.
    # and URL: 
    buzz = build('buzz', 'v1', http=self.http)
    following = buzz.groups().get(userId='googlebuzz', groupId='@following').execute()

    self.assertEquals(17, len(following))

if __name__ == '__main__':
  unittest.main()
