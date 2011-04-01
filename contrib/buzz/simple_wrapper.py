#!/usr/bin/python2.4
#
# Copyright (C) 2010 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'ade@google.com (Ade Oshineye)'

import apiclient.discovery
import httplib2
import logging

class SimpleWrapper(object):
  "Simple client that exposes the bare minimum set of common Buzz operations"

  def __init__(self, api_key=None, credentials=None):
    self.http = httplib2.Http()
    if credentials:
      logging.debug('Using api_client with credentials')
      self.http = credentials.authorize(self.http)
      self.api_client = apiclient.discovery.build('buzz', 'v1', http=self.http, developerKey=api_key)
    else:
      logging.debug('Using api_client that doesn\'t have credentials')
      self.api_client = apiclient.discovery.build('buzz', 'v1', http=self.http, developerKey=api_key)

  def search(self, query, user_token=None, max_results=10):
    if query is None or query.strip() is '':
      return None

    json = self.api_client.activities().search(q=query, max_results=max_results).execute()
    if json.has_key('items'):
      return json['items']
    return []

  def post(self, message_body, user_id='@me'):
    if message_body is None or message_body.strip() is '':
      return None

    activities = self.api_client.activities()
    logging.info('Retrieved activities for: %s' % user_id)
    activity = activities.insert(userId=user_id, body={
      'data' : {
        'title': message_body,
        'object': {
          'content': message_body,
          'type': 'note'}
       }
    }
                                 ).execute()
    url = activity['links']['alternate'][0]['href']
    logging.info('Just created: %s' % url)
    return url

  def get_profile(self, user_id='@me'):
    user_profile_data = self.api_client.people().get(userId=user_id).execute()
    return user_profile_data
  
  def get_follower_count(self, user_id='@me'):
    return self.__get_group_count(user_id, '@followers')
  
  def get_following_count(self, user_id='@me'):
    return self.__get_group_count(user_id, '@following')

  def __get_group_count(self, user_id, group_id):
    # Fetching 0 results is a performance optimisation that minimises the 
    # amount of data that's getting retrieved from the server
    cmd = self.api_client.people().list(userId=user_id, groupId=group_id,
                                        max_results=0)
    members = cmd.execute()
    if 'totalResults' not in members.keys():
      return -1
    return members['totalResults']
