# Copyright 2012 Google Inc.
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
"""Tests for oauth2client.xsrfutil.

Unit tests for oauth2client.xsrfutil.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import unittest

from oauth2client import xsrfutil

# Jan 17 2008, 5:40PM
TEST_KEY = 'test key'
TEST_TIME = 1200609642081230
TEST_USER_ID_1 = 123832983
TEST_USER_ID_2 = 938297432
TEST_ACTION_ID_1 = 'some_action'
TEST_ACTION_ID_2 = 'some_other_action'
TEST_EXTRA_INFO_1 = 'extra_info_1'
TEST_EXTRA_INFO_2 = 'more_extra_info'


class XsrfUtilTests(unittest.TestCase):
  """Test xsrfutil functions."""

  def testGenerateAndValidateToken(self):
    """Test generating and validating a token."""
    token = xsrfutil.generate_token(TEST_KEY,
                                   TEST_USER_ID_1,
                                   action_id=TEST_ACTION_ID_1,
                                   when=TEST_TIME)

    # Check that the token is considered valid when it should be.
    self.assertTrue(xsrfutil.validate_token(TEST_KEY,
                                           token,
                                           TEST_USER_ID_1,
                                           action_id=TEST_ACTION_ID_1,
                                           current_time=TEST_TIME))

    # Should still be valid 15 minutes later.
    later15mins = TEST_TIME + 15*60
    self.assertTrue(xsrfutil.validate_token(TEST_KEY,
                                           token,
                                           TEST_USER_ID_1,
                                           action_id=TEST_ACTION_ID_1,
                                           current_time=later15mins))

    # But not if beyond the timeout.
    later2hours = TEST_TIME + 2*60*60
    self.assertFalse(xsrfutil.validate_token(TEST_KEY,
                                            token,
                                            TEST_USER_ID_1,
                                            action_id=TEST_ACTION_ID_1,
                                            current_time=later2hours))

    # Or if the key is different.
    self.assertFalse(xsrfutil.validate_token('another key',
                                            token,
                                            TEST_USER_ID_1,
                                            action_id=TEST_ACTION_ID_1,
                                            current_time=later15mins))

    # Or the user ID....
    self.assertFalse(xsrfutil.validate_token(TEST_KEY,
                                            token,
                                            TEST_USER_ID_2,
                                            action_id=TEST_ACTION_ID_1,
                                            current_time=later15mins))

    # Or the action ID...
    self.assertFalse(xsrfutil.validate_token(TEST_KEY,
                                            token,
                                            TEST_USER_ID_1,
                                            action_id=TEST_ACTION_ID_2,
                                            current_time=later15mins))

    # Invalid when truncated
    self.assertFalse(xsrfutil.validate_token(TEST_KEY,
                                            token[:-1],
                                            TEST_USER_ID_1,
                                            action_id=TEST_ACTION_ID_1,
                                            current_time=later15mins))

    # Invalid with extra garbage
    self.assertFalse(xsrfutil.validate_token(TEST_KEY,
                                            token + 'x',
                                            TEST_USER_ID_1,
                                            action_id=TEST_ACTION_ID_1,
                                            current_time=later15mins))

    # Invalid with token of None
    self.assertFalse(xsrfutil.validate_token(TEST_KEY,
                                             None,
                                             TEST_USER_ID_1,
                                             action_id=TEST_ACTION_ID_1))

if __name__ == '__main__':
  unittest.main()
