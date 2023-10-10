# Copyright 2023 Google Inc. All rights reserved.
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

"""Unit tests for describe"""

import unittest
from googleapiclient import describe


# run this test file using nox -s "unit-3.8(oauth2client=None)" -- -k test_describe.py

class TestDescribe(unittest.TestCase):
    def test_example(self):
        self.assertTrue(describe.safe_version("testingv1.3") == "testingv1_3")


if __name__ == "__main__":
    unittest.main()
