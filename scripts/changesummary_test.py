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

import pathlib
import shutil
import unittest

import pandas as pd

from changesummary import ChangeSummary
from changesummary import ChangeType
from changesummary import DirectoryDoesNotExist

SCRIPTS_DIR = pathlib.Path(__file__).parent.resolve()
NEW_ARTIFACTS_DIR = SCRIPTS_DIR / "test_resources" / "new_artifacts_dir"
CURRENT_ARTIFACTS_DIR = SCRIPTS_DIR / "test_resources" / "current_artifacts_dir"
TEMP_DIR = SCRIPTS_DIR / "test_resources" / "temp"


class TestChangeSummary(unittest.TestCase):
    def setUp(self):
        # Clear temporary directory
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
        # Create temporary directory
        pathlib.Path(TEMP_DIR).mkdir()

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
        pathlib.Path(TEMP_DIR).mkdir()

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
        doc_path = NEW_ARTIFACTS_DIR / "drive.v3.json"
        df = self.cs._load_json_to_dataframe(file_path=doc_path)
        self.assertEqual(df["name"].iloc[0], "drive")
        self.assertEqual(df["version"].iloc[0], "v3")

    def test_get_discovery_differences_for_new_doc_returns_expected_dataframe(self):
        df = self.cs._get_discovery_differences("drive.v3.json")
        # Assume that `drive.v3.json` is a new discovery artifact that doesn't
        # exist in `CURRENT_ARTIFACTS_DIR`.
        self.assertEqual(df["Name"].iloc[0], "drive")
        self.assertEqual(df["Version"].iloc[0], "v3")

        # All rows in the dataframe should  have `True` in the `Added` column
        # and `False` in the `Deleted` column.
        # pd.Dataframe().all() will return `True` if all elements are `True`.
        self.assertTrue(df["Added"].all())
        self.assertTrue((~df["Deleted"]).all())

        # There should be 4 unique key differences
        self.assertEqual(len(df), 4)

        # Expected Result for key 'schemas.FileList'
        # Key            Added   Deleted  Name   Version  ChangeType  Count
        # schemas.FileList   True    False  drive      v3           2      8
        self.assertTrue(df[df["Key"] == "schemas.FileList"].Added.iloc[0])
        self.assertFalse(df[df["Key"] == "schemas.FileList"].Deleted.iloc[0])
        self.assertEqual(
            df[df["Key"] == "schemas.FileList"].ChangeType.iloc[0], ChangeType.ADDED
        )
        self.assertEqual(df[df["Key"] == "schemas.FileList"].Count.iloc[0], 8)

    def test_get_discovery_differences_for_deleted_doc_returns_expected_dataframe(self):
        df = self.cs._get_discovery_differences("cloudtasks.v2.json")
        # Assuming that `cloudtasks.v2.json` is a discovery artifact that doesn't
        # exist in `NEW_ARTIFACTS_DIR`.
        self.assertEqual(df["Name"].iloc[0], "cloudtasks")
        self.assertEqual(df["Version"].iloc[0], "v2")

        # All rows in the dataframe should have `False` in the `Added` column
        # and `True` in the `Deleted` column.
        # pd.Dataframe().all() will return `True` if all elements are `True`.
        self.assertTrue((~df["Added"]).all())
        self.assertTrue(df["Deleted"].all())

        # There should be 6 unique key differences
        self.assertEqual(len(df), 6)

        # Expected Result for key 'schemas.Task'
        # Key           Added   Deleted Name        Version  ChangeType  Count
        # schemas.Task  False     True  cloudtasks      v2           1     18
        self.assertFalse(df[df["Key"] == "schemas.Task"].Added.iloc[0])
        self.assertTrue(df[df["Key"] == "schemas.Task"].Deleted.iloc[0])
        self.assertEqual(
            df[df["Key"] == "schemas.Task"].ChangeType.iloc[0], ChangeType.DELETED
        )
        self.assertEqual(df[df["Key"] == "schemas.Task"].Count.iloc[0], 18)

    def test_get_discovery_differences_for_changed_doc_returns_expected_dataframe(self):
        # Assuming that `bigquery.v2.json` is a discovery artifact has
        # changed. There will be a mix of keys being added, changed or deleted.
        df = self.cs._get_discovery_differences("bigquery.v2.json")

        self.assertEqual(df["Name"].iloc[0], "bigquery")
        self.assertEqual(df["Version"].iloc[0], "v2")

        # There should be 28 unique key differences
        # 1 unique keys changed, 1 unique keys added, 2 unique keys deleted
        self.assertEqual(len(df), 4)
        self.assertEqual(len(df[df["ChangeType"] == ChangeType.CHANGED]), 1)
        self.assertEqual(len(df[df["ChangeType"] == ChangeType.ADDED]), 1)
        self.assertEqual(len(df[df["ChangeType"] == ChangeType.DELETED]), 2)

        # Expected Result for key 'schemas.PrincipalComponentInfo'
        # Key                             Added  Deleted  Name     Version  ChangeType  Count
        # schemas.PrincipalComponentInfo  False     True  bigquery v2            1     10
        key = "schemas.PrincipalComponentInfo"
        self.assertFalse(df[df["Key"] == key].Added.iloc[0])
        self.assertTrue(df[df["Key"] == key].Deleted.iloc[0])
        self.assertEqual(df[df["Key"] == key].ChangeType.iloc[0], ChangeType.DELETED)
        self.assertEqual(df[df["Key"] == key].Count.iloc[0], 10)

    def test_build_summary_message_returns_expected_result(self):
        msg = self.cs._build_summary_message(api_name="bigquery", is_feature=True)
        self.assertEqual(msg, "feat(bigquery): update the api")
        msg = self.cs._build_summary_message(api_name="bigquery", is_feature=False)
        self.assertEqual(msg, "fix(bigquery): update the api")

    def test_get_stable_versions(self):
        # These versions should be considered stable
        s = pd.Series(["v1", "v1.4", "v1.4.5"])
        self.assertTrue(self.cs._get_stable_versions(s).all().iloc[0])

        # These versions should not be considered stable
        s = pd.Series(["v1b1", "v1alpha", "v1beta1"])
        self.assertTrue((~self.cs._get_stable_versions(s)).all().iloc[0])

    def test_detect_discovery_changes(self):
        files_changed = ["bigquery.v2.json", "cloudtasks.v2.json", "drive.v3.json"]
        cs = ChangeSummary(
            NEW_ARTIFACTS_DIR, CURRENT_ARTIFACTS_DIR, TEMP_DIR, files_changed
        )
        cs.detect_discovery_changes()
        result = pd.read_csv(TEMP_DIR / "allapis.dataframe")

        # bigquery was added
        # 4 key changes in total.
        # 1 unique keys changed, 1 unique keys added, 2 unique keys deleted
        self.assertEqual(len(result[result["Name"] == "bigquery"]), 4)
        self.assertEqual(
            len(result[(result["Name"] == "bigquery") & result["Added"]]), 1
        )

        # Confirm that key "schemas.ProjectReference.newkey" exists for bigquery
        self.assertEqual(
            result[
                (result["Name"] == "bigquery") & (result["Added"]) & (result["Count"] == 1)
            ]["Key"].iloc[0],
            "schemas.ProjectReference.newkey",
        )

        self.assertEqual(
            len(result[(result["Name"] == "bigquery") & result["Deleted"]]), 2
        )
        self.assertTrue(result[result["Name"] == "bigquery"].IsStable.all())
        self.assertTrue(result[result["Name"] == "bigquery"].IsFeatureAggregate.all())
        self.assertEqual(
            result[result["Name"] == "bigquery"].Summary.iloc[0],
            "feat(bigquery): update the api",
        )

        # cloudtasks was deleted
        # 6 key changes in total. All 6 key changes should be deletions.
        self.assertEqual(len(result[result["Name"] == "cloudtasks"]), 6)
        self.assertEqual(
            len(result[(result["Name"] == "cloudtasks") & result["Added"]]), 0
        )
        self.assertEqual(
            len(result[(result["Name"] == "cloudtasks") & result["Deleted"]]), 6
        )
        self.assertTrue(result[(result["Name"] == "cloudtasks")].IsStable.all())
        self.assertTrue(
            result[(result["Name"] == "cloudtasks")].IsFeatureAggregate.all()
        )
        self.assertEqual(
            result[(result["Name"] == "cloudtasks")].Summary.iloc[0],
            "feat(cloudtasks): update the api",
        )

        # drive was updated
        # 4 key changes in total. All 4 key changes should be additions
        self.assertEqual(len(result[result["Name"] == "drive"]), 4)
        self.assertEqual(len(result[(result["Name"] == "drive") & result["Added"]]), 4)
        self.assertEqual(
            len(result[(result["Name"] == "drive") & result["Deleted"]]), 0
        )
        self.assertTrue(result[(result["Name"] == "drive")].IsStable.all())
        self.assertTrue(result[(result["Name"] == "drive")].IsFeatureAggregate.all())
        self.assertEqual(
            result[(result["Name"] == "drive")].Summary.iloc[0],
            "feat(drive): update the api",
        )


if __name__ == "__main__":
    unittest.main()
