#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""Discovery document tests

Functional tests that verify we can retrieve data from existing services.
"""

__author__ = 'ade@google.com (Ade Oshineye)'

import httplib2
import pprint

from apiclient.discovery import build
import httplib2
import logging
import pickle
import os
import time
import unittest

class BuzzFunctionalTest(unittest.TestCase):
  def setUp(self):
    self.buzz = build('buzz', 'v1', developerKey='AIzaSyD7aEm5tyC9BAdoC-MfL0ol7VV1P4zQgig')

  def test_can_get_specific_activity(self):
    activity = self.buzz.activities().get(userId='105037104815911535953',
                                     postId='B:z12sspviqyakfvye123wehng0muwz5jzq04').execute()

    self.assertTrue(activity is not None)

  def test_can_get_specific_activity_with_tag_id(self):
    activity = self.buzz.activities().get(userId='105037104815911535953',
                                     postId='tag:google.com,2010:buzz:z13ptnw5usmnv15ey22fzlswnuqoebasu').execute()

    self.assertTrue(activity is not None)

  def test_can_get_buzz_activities_with_many_params(self):
    max_results = 2
    activities_command = self.buzz.activities()
    activities = activities_command.list(userId='googlebuzz', scope='@self',
                             max_comments=max_results*2 ,max_liked=max_results*3,
                             max_results=max_results).execute()
    activity_count = len(activities['items'])
    self.assertEquals(max_results, activity_count)

    activities = activities_command.list_next(activities).execute()
    activity_count = len(activities['items'])
    self.assertEquals(max_results, activity_count)

  def test_can_get_multiple_pages_of_buzz_activities(self):
    max_results = 2
    activities_command = self.buzz.activities()

    activities = activities_command.list(userId='adewale', scope='@self',
                             max_results=max_results).execute()
    for count in range(10):
      activities = activities_command.list_next(activities).execute()
      activity_count = len(activities['items'])
      self.assertEquals(max_results, activity_count, 'Failed after %s pages' % str(count))

  def IGNORE_test_can_get_multiple_pages_of_buzz_likers(self):
    # Ignore this test until the Buzz API fixes the bug with next links
    # http://code.google.com/p/google-buzz-api/issues/detail?id=114
    max_results = 1
    people_cmd = self.buzz.people()
    # The post https://www.googleapis.com/buzz/v1/activities/111062888259659218284/@self/B:z13nh535yk2syfob004cdjyb3mjeulcwv3c?alt=json#
    #Perform this call https://www.googleapis.com/buzz/v1/activities/111062888259659218284/@self/B:z13nh535yk2syfob004cdjyb3mjeulcwv3c/@liked?alt=json&max-results=1
    people = people_cmd.liked(groupId='@liked', userId='googlebuzz', scope='@self',
                              postId='B:z13nh535yk2syfob004cdjyb3mjeulcwv3c', max_results=max_results).execute()

    for count in range(10):
      print count
      people = people_cmd.liked_next(people).execute()
      people_count = len(people['items'])
      self.assertEquals(max_results, people_count, 'Failed after %s pages' % str(count))

  def test_can_get_user_profile(self):
    person = self.buzz.people().get(userId='googlebuzz').execute()

    self.assertTrue(person is not None)
    self.assertEquals('buzz#person', person['kind'])
    self.assertEquals('Google Buzz Team', person['displayName'])
    self.assertEquals('111062888259659218284', person['id'])
    self.assertEquals('https://profiles.google.com/googlebuzz', person['profileUrl'])

  def test_can_get_user_profile_using_numeric_identifier(self):
    person = self.buzz.people().get(userId='108242092577082601423').execute()

    self.assertTrue(person is not None)
    self.assertEquals('buzz#person', person['kind'])
    self.assertEquals('Test Account', person['displayName'])
    self.assertEquals('108242092577082601423', person['id'])
    self.assertEquals('https://profiles.google.com/108242092577082601423', person['profileUrl'])

  def test_can_get_followees_of_user(self):
    expected_followees = 30
    following = self.buzz.people().list(userId='googlebuzz', groupId='@following', max_results=expected_followees).execute()

    self.assertEquals(expected_followees, following['totalResults'])
    self.assertEquals(expected_followees, len(following['entry']))

  def test_can_efficiently_get_follower_count_of_user(self):

    # Restricting max_results to 1 means only a tiny amount of data comes back but the totalResults still has the total.
    followers = self.buzz.people().list(userId='googlebuzz', groupId='@followers',
                                   max_results='1').execute()

    # @googlebuzz has a large but fluctuating number of followers
    # It is sufficient if the result is bigger than 10, 000
    follower_count = followers['totalResults']
    self.assertTrue(follower_count > 10000, follower_count)

  def test_follower_count_is_missing_for_user_with_hidden_follower_count(self):
    followers = self.buzz.people().list(userId='adewale', groupId='@followers').execute()

    self.assertFalse('totalResults' in followers)


class BuzzAuthenticatedFunctionalTest(unittest.TestCase):
  def __init__(self, method_name):
    unittest.TestCase.__init__(self, method_name)
    credentials_dir = os.path.join(logging.os.path.dirname(__file__), './data')
    f = file(os.path.join(credentials_dir, 'buzz_credentials.dat'), 'r')
    credentials = pickle.loads(f.read())
    f.close()

    self.http = credentials.authorize(httplib2.Http())
    self.buzz = build('buzz', 'v1', http=self.http, developerKey='AIzaSyD7aEm5tyC9BAdoC-MfL0ol7VV1P4zQgig')

  def test_can_create_activity(self):

    activity = self.buzz.activities().insert(userId='@me', body={
        'data': {
            'title': 'Testing insert',
            'object': {
                'content': u'Just a short note to show that insert is working. ?',
                'type': 'note'}
            }
        }
    ).execute()
    self.assertTrue(activity is not None)

  def test_fields_parameter_restricts_response_fields(self):
    activity = self.buzz.activities().insert(userId='@me', body={
        'data': {
            'title': 'Testing patch',
            'object': {
                'content': u'Just a short note to show that insert is working. ?',
                'type': 'note'}
            }
        }
    ).execute()
    self.assertTrue('kind' in activity)

    # test fields to restrict what is returned
    activity = self.buzz.activities().get(userId='@me', postId=activity['id'],
                                        fields='object,id').execute()
    self.assertTrue('kind' not in activity)
    self.assertTrue('object' in activity)
    self.assertTrue('id' in activity)

  def test_patch(self):
    activity = self.buzz.activities().insert(userId='@me', body={
        'data': {
            'title': 'Testing patch',
            'object': {
                'content': u'Just a short note to show that insert is working. ?',
                'type': 'note'}
            }
        }).execute()
    # Construct a raw patch to send, also restrict the response with fields
    activity = self.buzz.activities().patch(userId='@me',
                                            scope='@self',
                                            postId=activity['id'],
                                            body={
        'object': {
            'content': 'Updated content only!'}},
        fields='object').execute()
    self.assertEquals(activity['object']['content'], 'Updated content only!')
    self.assertTrue('id' not in activity)

  def test_can_create_private_activity(self):
    activity = self.buzz.activities().insert(userId='@me', body={
        'data': {
            'title': 'Testing insert',
            'object': {
                'content': 'This is a private post.'
                },
            'visibility': {
                'entries': [
                    { 'id': 'tag:google.com,2010:buzz-group:108242092577082601423:13' }
                    ]
                }
            }
        }
    ).execute()
    self.assertTrue(activity is not None)

  def test_can_create_and_delete_new_group(self):
    group_name = 'New Group Created At' + str(time.time())
    group = self.buzz.groups().insert(userId='@me', body = {
      'data': {
        'title': group_name
      }
    }).execute()
    self.assertTrue(group is not None)

    result = self.buzz.groups().delete(userId='@me', groupId=group['id']).execute()
    self.assertEquals({}, result)

  def test_can_identify_number_of_groups_belonging_to_user(self):
    groups = self.buzz.groups().list(userId='108242092577082601423').execute()

    # This should work as long as no-one deletes the 4 default groups for this test account
    expected_default_number_of_groups = 4
    self.assertTrue(len(groups['items']) > expected_default_number_of_groups)

  def IGNORE__test_can_like_activity(self):
    activity = self.buzz.activities().insert(userId='@me', body={
        'data': {
            'title': 'Testing insert',
            'object': {
                'content': u'Just a short note to show that insert is working. ?',
                'type': 'note'}
            }
        }
    ).execute()
    pprint.pprint(activity)
    id = activity['id']
    likers = self.buzz.people().liked(userId='105037104815911535953', postId=id, groupId='@liked', scope='@self').execute()
    # Todo(ade) Insert the new liker once the Buzz back-end bug is fixed

  def test_can_comment_on_activity(self):
    activity = self.buzz.activities().insert(userId='@me', body={
        'data': {
            'title': 'A new activity',
            'object': {
                'content': u'The body of the new activity',
                'type': 'note'}
            }
        }
    ).execute()

    id = activity['id']
    comment = self.buzz.comments().insert(userId='@me', postId=id, body={
        'data': {
            'content': 'A comment on the new activity'
            }
    }).execute()

  def test_can_list_groups_belonging_to_user(self):
    groups = self.buzz.groups().list(userId='108242092577082601423').execute()

    group = self.buzz.groups().get(userId='108242092577082601423', groupId='G:108242092577082601423:15').execute()
    self.assertEquals('G:108242092577082601423:15', group['id'], group)

    group = self.buzz.groups().get(userId='108242092577082601423', groupId='G:108242092577082601423:14').execute()
    self.assertEquals('G:108242092577082601423:14', group['id'], group)

    group = self.buzz.groups().get(userId='108242092577082601423', groupId='G:108242092577082601423:13').execute()
    self.assertEquals('G:108242092577082601423:13', group['id'], group)

    group = self.buzz.groups().get(userId='108242092577082601423', groupId='G:108242092577082601423:6').execute()
    self.assertEquals('G:108242092577082601423:6', group['id'], group)

  def test_can_delete_activity(self):
    activity = self.buzz.activities().insert(userId='@me', body={
        'data': {
            'title': 'Activity to be deleted',
            'object': {
                'content': u'Created this activity so that it can be deleted.',
                'type': 'note'}
            }
        }
    ).execute()
    id = activity['id']

    self.buzz.activities().delete(scope='@self', userId='@me', postId=id).execute()
    time.sleep(2)

    activity_url = activity['links']['self'][0]['href']
    resp, content = self.http.request(activity_url, 'GET')
    self.assertEquals(404, resp.status)

if __name__ == '__main__':
  unittest.main()
