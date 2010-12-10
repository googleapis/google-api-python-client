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