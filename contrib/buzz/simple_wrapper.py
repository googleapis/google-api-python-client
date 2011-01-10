#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc. All Rights Reserved.

__author__ = 'ade@google.com (Ade Oshineye)'

import apiclient.discovery
import httplib2
import logging

class SimpleWrapper(object):
  "Simple client that exposes the bare minimum set of common Buzz operations"

  def __init__(self, api_key=None, credentials=None):
    if credentials:
      logging.debug('Using api_client with credentials')
      http = httplib2.Http()
      http = credentials.authorize(http)
      self.api_client = apiclient.discovery.build('buzz', 'v1', http=http, developerKey=api_key)
    else:
      logging.debug('Using api_client that doesn\'t have credentials')
      self.api_client = apiclient.discovery.build('buzz', 'v1', developerKey=api_key)

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
