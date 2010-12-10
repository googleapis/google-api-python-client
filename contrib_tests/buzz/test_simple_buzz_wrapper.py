#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc. All Rights Reserved.

__author__ = 'ade@google.com (Ade Oshineye)'

from contrib.buzz.simple_buzz_wrapper import SimpleBuzzWrapper
import unittest

class SimpleBuzzWrapperTest(unittest.TestCase):
# None of these tests make a remote call. We assume the underlying libraries
# and servers are working.

  def test_wrapper_rejects_empty_post(self):
    wrapper = SimpleBuzzWrapper()
    self.assertEquals(None, wrapper.post('sender@example.org', ''))

  def test_wrapper_rejects_post_containing_only_whitespace(self):
    wrapper = SimpleBuzzWrapper()
    self.assertEquals(None, wrapper.post('sender@example.org', '            '))

  def test_wrapper_rejects_none_post(self):
    wrapper = SimpleBuzzWrapper()
    self.assertEquals(None, wrapper.post('sender@example.org', None))

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
	def test_searching_returns_results(self):
		wrapper = SimpleBuzzWrapper()
		results = wrapper.search('oshineye')
		self.assertTrue(results is not None)
	
	def test_searching_honours_max_results(self):
		wrapper = SimpleBuzzWrapper()
		max = 5
		results = wrapper.search('oshineye', max_results=max)
		self.assertEquals(max, len(results))
		
	def test_can_fetch_profile(self):
	  wrapper = SimpleBuzzWrapper()
	  profile = wrapper.get_profile('googlebuzz')
	  self.assertTrue(profile is not None)
	  
	  profile = wrapper.get_profile(user_id = 'adewale')
	  self.assertTrue(profile is not None)

if __name__ == '__main__':
  unittest.main()