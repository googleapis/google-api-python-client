#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc. All Rights Reserved.

__author__ = 'ade@google.com (Ade Oshineye)'

import buzz_gae_client
import logging

class SimpleBuzzWrapper(object):
  "Simple client that exposes the bare minimum set of common Buzz operations"

  def __init__(self, api_key=None, consumer_key='anonymous', consumer_secret='anonymous',
    oauth_token=None, oauth_token_secret=None):
    
    self.builder = buzz_gae_client.BuzzGaeClient(consumer_key, consumer_secret, api_key=api_key)
    if oauth_token and oauth_token_secret:
      logging.debug('Using api_client with authorisation')
      oauth_params_dict = {}
      oauth_params_dict['consumer_key'] = consumer_key
      oauth_params_dict['consumer_secret'] = consumer_secret
      oauth_params_dict['oauth_token'] = oauth_token
      oauth_params_dict['oauth_token_secret'] = oauth_token_secret
      self.api_client = self.builder.build_api_client(oauth_params=oauth_params_dict)
    else:
      logging.debug('Using api_client that doesn\'t have authorisation')
      self.api_client = self.builder.build_api_client()

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

