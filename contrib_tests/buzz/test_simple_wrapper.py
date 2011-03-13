#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc. All Rights Reserved.

__author__ = 'ade@google.com (Ade Oshineye)'

from contrib.buzz.simple_wrapper import SimpleWrapper

import apiclient.oauth
import httplib2
import logging
import oauth2 as oauth
import os
import pickle
import unittest

class SimpleWrapperTest(unittest.TestCase):
# None of these tests make a remote call. We assume the underlying libraries
# and servers are working.

  def test_wrapper_rejects_empty_post(self):
    wrapper = SimpleWrapper()
    self.assertEquals(None, wrapper.post('', '108242092577082601423'))

  def test_wrapper_rejects_post_containing_only_whitespace(self):
    wrapper = SimpleWrapper()
    self.assertEquals(None, wrapper.post('            ', '108242092577082601423'))

  def test_wrapper_rejects_none_post(self):
    wrapper = SimpleWrapper()
    self.assertEquals(None, wrapper.post(None, '108242092577082601423'))

  def test_wrapper_rejects_empty_search(self):
    wrapper = SimpleWrapper()
    self.assertEquals(None, wrapper.search(''))

  def test_wrapper_rejects_search_containing_only_whitespace(self):
    wrapper = SimpleWrapper()
    self.assertEquals(None, wrapper.search(' '))

  def test_wrapper_rejects_search_with_none(self):
    wrapper = SimpleWrapper()
    self.assertEquals(None, wrapper.search(None))
  
  def test_wrapper_returns_minus_one_for_hidden_follower_count(self):
    wrapper = SimpleWrapper()
    self.assertEquals(-1, wrapper.get_follower_count(user_id='108242092577082601423'))
  
  def test_wrapper_returns_positive_value_for_visible_follower_count(self):
    wrapper = SimpleWrapper()
    count = wrapper.get_follower_count(user_id='googlebuzz')
    self.assertTrue(count > 0, "Got %s instead" % count)
    
  def test_wrapper_returns_minus_one_for_hidden_following_count(self):
    wrapper = SimpleWrapper()
    self.assertEquals(-1, wrapper.get_following_count(user_id='108242092577082601423'))

  def test_wrapper_returns_positive_value_for_visible_following_count(self):
    wrapper = SimpleWrapper()
    count = wrapper.get_following_count(user_id='googlebuzz')
    self.assertTrue(count > 0, "Got %s instead" % count)

class SimpleWrapperRemoteTest(unittest.TestCase):
  # These tests make remote calls
  def __init__(self, method_name):
    unittest.TestCase.__init__(self, method_name)
    oauth_params_dict = {}
    for line in open('./contrib_tests/test_account.oacurl.properties'):
      line = line.strip()
      if line.startswith('#'):
        continue
      key,value = line.split('=')
      oauth_params_dict[key.strip()] = value.strip()

    consumer = oauth.Consumer(oauth_params_dict['consumerKey'],
                              oauth_params_dict['consumerSecret'])
    token = oauth.Token(oauth_params_dict['accessToken'],
                        oauth_params_dict['accessTokenSecret'])
    user_agent = 'google-api-client-python-buzz-webapp/1.0'
    credentials = apiclient.oauth.OAuthCredentials(consumer, token, user_agent)
    self.wrapper = SimpleWrapper(credentials=credentials)

  def test_searching_returns_results(self):
    results = self.wrapper.search('oshineye')
    self.assertTrue(results is not None)

  def test_searching_honours_max_results(self):
    max = 5
    results = self.wrapper.search('oshineye', max_results=max)
    self.assertEquals(max, len(results))

  def test_can_fetch_profile(self):
    profile = self.wrapper.get_profile('googlebuzz')
    self.assertTrue(profile is not None)

    profile = self.wrapper.get_profile(user_id='adewale')
    self.assertTrue(profile is not None)

  def test_can_post_without_user_id(self):
    url = self.wrapper.post('test message')
    self.assertTrue(url is not None)
    self.assertTrue(url.startswith('https://profiles.google.com/'), url)

  def test_can_post_with_user_id(self):
    url = self.wrapper.post('test message', '108242092577082601423')
    self.assertTrue(url is not None)
    self.assertTrue(url.startswith('https://profiles.google.com/'), url)

  def test_wrapper_returns_positive_value_for_hidden_follower_count_when_authorised(self):
    count = self.wrapper.get_follower_count(user_id='108242092577082601423')
    self.assertTrue(count > 0, "Got %s instead" % count)

  def test_wrapper_returns_positive_value_for_hidden_following_count_when_authorised(self):
    count = self.wrapper.get_following_count(user_id='108242092577082601423')
    self.assertTrue(count > 0, "Got %s instead" % count)

if __name__ == '__main__':
  unittest.main()