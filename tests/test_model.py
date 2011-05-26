#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc.
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

"""Model tests

Unit tests for model utility methods.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

import httplib2
import unittest

from apiclient.model import makepatch


TEST_CASES = [
    # (message, original, modified, expected)
    ("Remove an item from an object",
     {'a': 1, 'b': 2},  {'a': 1},         {'b': None}),
    ("Add an item to an object",
     {'a': 1},          {'a': 1, 'b': 2}, {'b': 2}),
    ("No changes",
     {'a': 1, 'b': 2},  {'a': 1, 'b': 2}, {}),
    ("Empty objects",
     {},  {}, {}),
    ("Modify an item in an object",
     {'a': 1, 'b': 2},  {'a': 1, 'b': 3}, {'b': 3}),
    ("Change an array",
     {'a': 1, 'b': [2, 3]},  {'a': 1, 'b': [2]}, {'b': [2]}),
    ("Modify a nested item",
     {'a': 1, 'b': {'foo':'bar', 'baz': 'qux'}},
     {'a': 1, 'b': {'foo':'bar', 'baz': 'qaax'}},
     {'b': {'baz': 'qaax'}}),
    ("Modify a nested array",
     {'a': 1, 'b': [{'foo':'bar', 'baz': 'qux'}]},
     {'a': 1, 'b': [{'foo':'bar', 'baz': 'qaax'}]},
     {'b': [{'foo':'bar', 'baz': 'qaax'}]}),
    ("Remove item from a nested array",
     {'a': 1, 'b': [{'foo':'bar', 'baz': 'qux'}]},
     {'a': 1, 'b': [{'foo':'bar'}]},
     {'b': [{'foo':'bar'}]}),
    ("Remove a nested item",
     {'a': 1, 'b': {'foo':'bar', 'baz': 'qux'}},
     {'a': 1, 'b': {'foo':'bar'}},
     {'b': {'baz': None}})
]


class TestPatch(unittest.TestCase):

  def test_patch(self):
    for (msg, orig, mod, expected_patch) in TEST_CASES:
      self.assertEqual(expected_patch, makepatch(orig, mod), msg=msg)


if __name__ == '__main__':
  unittest.main()
