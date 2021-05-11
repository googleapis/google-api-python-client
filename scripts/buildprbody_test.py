# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""BuildPrBody tests."""

__author__ = "partheniou@google.com (Anthonios Partheniou)"

import pathlib
import shutil
import unittest

from buildprbody import BuildPrBody
from changesummary import ChangeType

SCRIPTS_DIR = pathlib.Path(__file__).parent.resolve()
CHANGE_SUMMARY_DIR = SCRIPTS_DIR / "test_resources" / "buildprbody_resources"

EXPECTED_PR_BODY_OUTPUT = """\
## Deleted keys were detected in the following stable discovery artifacts:
bigquery v2 https://github.com/googleapis/google-api-python-client/commit/123
cloudtasks v2 https://github.com/googleapis/google-api-python-client/commit/456

## Discovery Artifact Change Summary:
feat(bigquery): update the api https://github.com/googleapis/google-api-python-client/commit/123
feat(cloudtasks): update the api https://github.com/googleapis/google-api-python-client/commit/456
feat(drive): update the api https://github.com/googleapis/google-api-python-client/commit/789
"""


class TestBuildPrBody(unittest.TestCase):
    def setUp(self):
        self.buildprbody = BuildPrBody(change_summary_directory=CHANGE_SUMMARY_DIR)

    def test_get_commit_uri_returns_correct_string(self):
        base_uri = "https://github.com/googleapis/google-api-python-client/commit/"

        expected_uri = "".join([base_uri, "123"])
        result = self.buildprbody.get_commit_uri(name="bigquery")
        self.assertEqual(result, expected_uri)

        expected_uri = "".join([base_uri, "456"])
        result = self.buildprbody.get_commit_uri(name="cloudtasks")
        self.assertEqual(result, expected_uri)

        expected_uri = "".join([base_uri, "789"])
        result = self.buildprbody.get_commit_uri(name="drive")
        self.assertEqual(result, expected_uri)

    def test_generate_pr_body(self):
        self.buildprbody.generate_pr_body()

        with open(CHANGE_SUMMARY_DIR / "allapis.summary") as f:
            pr_body = "".join(f.readlines())
        self.assertEqual(pr_body, EXPECTED_PR_BODY_OUTPUT)
