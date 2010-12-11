#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc. All Rights Reserved.

__author__ = 'ade@google.com (Ade Oshineye)'

from contrib.buzz.simple_buzz_wrapper import SimpleBuzzWrapper

import httplib2
import logging
import os
import pickle
import unittest

class SimpleBuzzWrapperTest(unittest.TestCase):
# None of these tests make a remote call. We assume the underlying libraries
# and servers are working.

  def test_wrapper_rejects_empty_post(self):
    wrapper = SimpleBuzzWrapper()
    self.assertEquals(None, wrapper.post('', '108242092577082601423'))

  def test_wrapper_rejects_post_containing_only_whitespace(self):
    wrapper = SimpleBuzzWrapper()
    self.assertEquals(None, wrapper.post('            ', '108242092577082601423'))

  def test_wrapper_rejects_none_post(self):
    wrapper = SimpleBuzzWrapper()
    self.assertEquals(None, wrapper.post(None, '108242092577082601423'))

  def test_wrapper_rejects_empty_search(self):
    wrapper = SimpleBuzzWrapper()
    self.assertEquals(None, wrapper.search(''))

  def test_wrapper_rejects_search_containing_only_whitespace(self):
    wrapper = SimpleBuzzWrapper()
    self.assertEquals(None, wrapper.search(' '))

  def test_wrapper_rejects_search_with_none(self):
    wrapper = SimpleBuzzWrapper()
    self.assertEquals(None, wrapper.search(None))

class SimpleBuzzWrapperRemoteTest(unittest.TestCase):
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

    self.wrapper = SimpleBuzzWrapper(consumer_key=oauth_params_dict['consumerKey'],
      consumer_secret=oauth_params_dict['consumerSecret'], oauth_token=oauth_params_dict['accessToken'], 
      oauth_token_secret=oauth_params_dict['accessTokenSecret'])

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
    self.assertTrue(url.startswith('http://www.google.com/buzz/'))

  def test_can_post_with_user_id(self):
    url = self.wrapper.post('test message', '108242092577082601423')
    self.assertTrue(url is not None)
    self.assertTrue(url.startswith('http://www.google.com/buzz/'))

if __name__ == '__main__':
  unittest.main()