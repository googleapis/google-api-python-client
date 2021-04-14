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

"""ChangeSummary tests."""

__author__ = "partheniou@google.com (Anthonios Partheniou)"

import os
import shutil
import unittest

import numpy as np
import pandas as pd

from changesummary import ChangeSummary
from changesummary import ChangeType
from changesummary import DirectoryDoesNotExist


SCRIPTS_DIR = os.path.dirname(os.path.realpath(__file__))
NEW_ARTIFACTS_DIR = os.path.join(SCRIPTS_DIR, "test_resources", "new_artifacts_dir")
CURRENT_ARTIFACTS_DIR = os.path.join(
    SCRIPTS_DIR, "test_resources", "current_artifacts_dir"
)
TEMP_DIR = os.path.join(SCRIPTS_DIR, "test_resources", "temp")


class TestChangeSummary(unittest.TestCase):
    def setUp(self):
        # Create temporary directory
        os.mkdir(TEMP_DIR)

        self.cs = ChangeSummary(NEW_ARTIFACTS_DIR, CURRENT_ARTIFACTS_DIR, TEMP_DIR, [])

    def test_raises_on_directory_not_found_new_artifacts_dir(self):
        with self.assertRaises(DirectoryDoesNotExist):
            ChangeSummary(
                "invalid_artifact_dir", CURRENT_ARTIFACTS_DIR, TEMP_DIR, []
            ).detect_discovery_changes()

    def test_raises_on_directory_not_found_current_artifacts_dir(self):
        with self.assertRaises(DirectoryDoesNotExist):
            ChangeSummary(
                NEW_ARTIFACTS_DIR, "invalid_artifact_dir", TEMP_DIR, []
            ).detect_discovery_changes()

    def test_raises_on_directory_not_found_temp_dir(self):
        # Remove temporary directory
        shutil.rmtree(TEMP_DIR, ignore_errors=True)

        with self.assertRaises(DirectoryDoesNotExist):
            ChangeSummary(
                NEW_ARTIFACTS_DIR, CURRENT_ARTIFACTS_DIR, "invalid_temp_dir", []
            ).detect_discovery_changes()

        # Create temporary directory
        os.mkdir(TEMP_DIR)

        ChangeSummary(
            NEW_ARTIFACTS_DIR, CURRENT_ARTIFACTS_DIR, TEMP_DIR, []
        ).detect_discovery_changes()

    def test_raises_on_directory_not_found(self):
        with self.assertRaises(DirectoryDoesNotExist):
            self.cs._raise_if_directory_not_found(directory="invalid_dir")

    def test_load_json_to_dataframe_returns_empty_df_if_file_path_invalid(self):
        df = self.cs._load_json_to_dataframe(file_path="invalid_path")
        self.assertTrue(df.empty)

    def test_load_json_to_dataframe_returns_expected_data(self):
        doc_path = os.path.join(NEW_ARTIFACTS_DIR, "drive.v3.json")
        df = self.cs._load_json_to_dataframe(file_path=doc_path)
        self.assertEqual(df["name"][0], "drive")
        self.assertEqual(df["version"][0], "v3")

    def test_get_discovery_differences_for_new_doc_returns_expected_dataframe(self):
        df = self.cs._get_discovery_differences("drive.v3.json")
        # Assume that `drive.v3.json` is a new discovery artifact that doesn't
        # exist in `CURRENT_ARTIFACTS_DIR`. All rows in the dataframe should
        # have `True` in the `Added` column and `False` in the `Deleted` column.

        self.assertEqual(df["Name"].drop_duplicates().values, ["drive"])
        self.assertEqual(df["Version"].drop_duplicates().values, ["v3"])
        self.assertEqual(df["Added"].drop_duplicates().values, [True])
        self.assertEqual(df["Deleted"].drop_duplicates().values, [False])
        self.assertEqual(df["ChangeType"].drop_duplicates().values, [ChangeType.ADDED])

        # There should be 74 unique key differences
        self.assertEqual(len(df), 74)

        # Expected Result for key 'schemas.File'
        # Key            Added   Deleted  Name   Version  ChangeType  Count
        # schemas.File   True    False    drive      v3           2    168
        self.assertEqual(df[df["Key"] == "schemas.File"].Count.iloc[0], 168)

    def test_get_discovery_differences_for_deleted_doc_returns_expected_dataframe(self):
        df = self.cs._get_discovery_differences("cloudtasks.v2.json")
        # Assuming that `cloudtasks.v2.json` is a discovery artifact that doesn't
        # exist in `NEW_ARTIFACTS_DIR`. All rows in the dataframe should have
        # `False` in the `Added` column and `True` in the `Deleted` column.

        self.assertEqual(df["Name"].drop_duplicates().values, ["cloudtasks"])
        self.assertEqual(df["Version"].drop_duplicates().values, ["v2"])
        self.assertEqual(df["Added"].drop_duplicates().values, [False])
        self.assertEqual(df["Deleted"].drop_duplicates().values, [True])
        self.assertEqual(
            df["ChangeType"].drop_duplicates().values, [ChangeType.DELETED]
        )

        # There should be 72 unique key differences
        self.assertEqual(len(df), 72)

        # Expected Result for key 'schemas.Task'
        # Key           Added   Deleted Name        Version  ChangeType  Count
        # schemas.Task  False     True  cloudtasks      v2           1     18
        self.assertEqual(df[df["Key"] == "schemas.Task"].Count.iloc[0], 18)

    def test_get_discovery_differences_for_changed_doc_returns_expected_dataframe(self):
        df = self.cs._get_discovery_differences("bigquery.v2.json")
        # Assuming that `bigquery.v2.json` is a discovery artifact has
        # changed.

        self.assertEqual(df["Name"].drop_duplicates().values, ["bigquery"])
        self.assertEqual(df["Version"].drop_duplicates().values, ["v2"])
        # There should be a mix of Added and Deleted Keys
        self.assertEqual(df["Added"].drop_duplicates().values.all(),
            np.array([False, True]).all(),
        )
        self.assertEqual(df["Deleted"].drop_duplicates().values.all(),
            np.array([False, True]).all(),
        )
        self.assertEqual(
            df["ChangeType"].drop_duplicates().values.all(),
            np.array([ChangeType.CHANGED, ChangeType.ADDED, ChangeType.DELETED]).all()
        )

        # There should be 28 unique key differences
        self.assertEqual(len(df), 28)

        # 11 unique keys changed
        self.assertEqual(len(df[df["ChangeType"] == ChangeType.CHANGED]), 11)

        # 13 unique keys added
        self.assertEqual(len(df[df["ChangeType"] == ChangeType.ADDED]), 13)

        # 4 unique keys deleted
        self.assertEqual(len(df[df["ChangeType"] == ChangeType.DELETED]), 4)

        # Expected Result for key 'schemas.PrincipalComponentInfo'
        # Key                             Added  Deleted  Name     Version  ChangeType  Count
        # schemas.PrincipalComponentInfo  False     True  bigquery v2            1     10
        self.assertEqual(
            df[df["Key"] == "schemas.PrincipalComponentInfo"].Count.iloc[0], 10
        )


if __name__ == "__main__":
    unittest.main()
