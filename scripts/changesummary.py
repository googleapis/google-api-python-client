# Copyright 2021 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import IntEnum
import json
from multiprocessing import Pool
import pandas as pd
import pathlib
import numpy as np

BRANCH_ARTIFACTS_DIR = (
    pathlib.Path(__file__).parent.resolve()
    / "googleapiclient"
    / "discovery_cache"
    / "documents"
)
MAIN_ARTIFACTS_DIR = (
    pathlib.Path(__file__).parent.resolve()
    / ".."
    / "main"
    / "googleapiclient"
    / "discovery_cache"
    / "documents"
)

MULTIPROCESSING_NUM_PER_BATCH = 5
MULTIPROCESSING_NUM_AGENTS = 10


class ChangeType(IntEnum):
    UNKNOWN = 0
    DELETED = 1
    ADDED = 2
    CHANGED = 3


class DirectoryDoesNotExist(ValueError):
    """Raised when the specified directory does not exist."""

    pass


class ChangeSummary:
    """Represents the change summary between 2 directories containing \
        artifacts.
    """

    def __init__(self, new_artifacts_dir, current_artifacts_dir, temp_dir, file_list):
        """Initializes an instance of a ChangeSummary.

        Args:
            new_artifacts_dir (str): The relative path to the directory with the
                new discovery artifacts.
            current_artifacts_dir (str): The relative path to the directory with
                the current discovery artifacts.
            temp_dir (str): The relative path to the directory used for
                temporary storage where intermediate files will be stored.
            file_list (list): A list of strings containing files to analyze.
        """

        self._file_list = file_list
        self._new_artifacts_dir = pathlib.Path(new_artifacts_dir)
        self._current_artifacts_dir = pathlib.Path(current_artifacts_dir)
        self._temp_dir = pathlib.Path(temp_dir)

        # Sanity checks to ensure directories exist
        self._raise_if_directory_not_found(self._new_artifacts_dir)
        self._raise_if_directory_not_found(self._current_artifacts_dir)
        self._raise_if_directory_not_found(self._temp_dir)

    def _raise_if_directory_not_found(self, directory):
        """Raises if the `directory` doesn't exist

        args:
            directory (str): The relative path to the `directory`
        """

        if not pathlib.Path(directory).exists():
            raise DirectoryDoesNotExist(
                "Directory does not exist : {0}".format(directory)
            )

    def _load_json_to_dataframe(self, file_path):
        """Returns a pandas dataframe from the json file provided.

        args:
            file_path (str): The relative path to the discovery artifact to
                parse.
        """

        # Create an empty dataframe as we will need to return it if the file
        # doesn't exist
        dataframe_doc = pd.DataFrame()

        if pathlib.Path(file_path).is_file():
            with open(file_path, "r") as f:
                # Now load the json file into a pandas dataframe as a flat table
                dataframe_doc = pd.json_normalize(json.load(f))
        return dataframe_doc

    def _get_discovery_differences(self, filename):
        """Returns a pandas dataframe which contains the differences with the
        current and new discovery artifact directories, corresponding to the
        file name provided.

        args:
            filename (str): The name of the discovery artifact to parse.
        """
        # The paths of the 2 discovery artifacts to compare
        current_artifact_path = self._current_artifacts_dir / filename
        new_artifact_path = self._new_artifacts_dir / filename

        # Use a helper functions to load the discovery artifacts into pandas
        # dataframes
        current_doc = self._load_json_to_dataframe(current_artifact_path)
        new_doc = self._load_json_to_dataframe(new_artifact_path)

        # Concatenate the 2 dataframes, transpose them, and create
        # a new dataframe called combined_docs with columns
        # `Key`, `CurrentValue`, `NewValue`.
        combined_docs = (
            pd.concat([current_doc, new_doc], keys=["CurrentValue", "NewValue"])
            # Drop the index column
            .reset_index(drop=True, level=1)
            # Transpose the DataFrame, Resulting Columns should be
            # ["Key", "CurrentValue", "New Value"]
            .rename_axis(["Key"], axis=1).transpose()
            # Drop the index column
            .reset_index()
        )

        # When discovery documents are added, the column `CurrentValue` will
        # not exist. In that case, we'll just populate with `np.nan`.
        if "CurrentValue" not in combined_docs.columns:
            combined_docs["CurrentValue"] = np.nan

        # When discovery documents are deleted, the column `NewValue` will
        # not exist. In that case, we'll just populate with `np.nan`.
        if "NewValue" not in combined_docs.columns:
            combined_docs["NewValue"] = np.nan

        # Split the Key into 2 columns for `Parent` and `Child` in order
        # to group keys with the same parents together to summarize the changes
        # by parent.
        parent_child_df = combined_docs["Key"].str.rsplit(".", 1, expand=True)
        # Rename the columns and join them with the combined_docs dataframe.
        # If we only have a `Parent` column, it means that the Key doesn't have
        # any children.
        if len(parent_child_df.columns) == 1:
            parent_child_df.columns = ["Parent"]
        else:
            parent_child_df.columns = ["Parent", "Child"]
        combined_docs = combined_docs.join(parent_child_df)

        # Create a new column `Added` to identify rows which have new keys.
        combined_docs["Added"] = np.where(
            combined_docs["CurrentValue"].isnull(), True, False
        )

        # Create a new column `Deleted` to identify rows which have deleted keys.
        combined_docs["Deleted"] = np.where(
            combined_docs["NewValue"].isnull(), True, False
        )

        # Aggregate the keys added by grouping keys with the same parents
        # together to summarize the changes by parent rather than by key.
        parent_added_agg = (
            combined_docs.groupby("Parent")
            .Added.value_counts(normalize=True)
            .reset_index(name="Proportion")
        )

        # Add a column NumLevels to inicate the number of levels in the tree
        # which will allow us to sort the parents in hierarchical order.
        parent_added_agg["NumLevels"] = (
            parent_added_agg["Parent"].str.split(".").apply(lambda x: len(x))
        )

        # Aggregate the keys deleted by grouping keys with the same parents
        # together to summarize the changes by parent rather than by key.
        parent_deleted_agg = (
            combined_docs.groupby("Parent")
            .Deleted.value_counts(normalize=True)
            .reset_index(name="Proportion")
        )

        # Add a column NumLevels to inicate the number of levels in the tree
        # which will allow us to sort the parents in hierarchical order.
        parent_deleted_agg["NumLevels"] = (
            parent_added_agg["Parent"].str.split(".").apply(lambda x: len(x))
        )

        # Create a list of all parents that have been added in hierarchical
        # order. When `Proportion` is 1, it means that the parent is new as all
        # children keys have been added.
        all_added = (
            parent_added_agg[
                (parent_added_agg["Proportion"] == 1)
                & (parent_added_agg["Added"] == True)
            ][["Parent", "NumLevels"]]
            .sort_values("NumLevels", ascending=True)
            .Parent.to_list()
        )

        # Create a list of all parents that have been deleted in hierarchical
        # order. When `Proportion` is 1, it means that the parent is new as all
        # children keys have been deleted.
        all_deleted = (
            parent_deleted_agg[
                (parent_deleted_agg["Proportion"] == 1)
                & (parent_deleted_agg["Deleted"] == True)
            ][["Parent", "NumLevels"]]
            .sort_values("NumLevels", ascending=True)
            .Parent.to_list()
        )

        # Go through the list of parents that have been added. If we find any
        # keys with parents which are a substring of the parent in this list,
        # then it means that the entire parent is new. We don't need verbose
        # information about the children, so we replace the parent.
        for i in range(0, len(all_added)):
            word = all_added[i]
            combined_docs.Parent = np.where(
                combined_docs["Parent"].str.startswith(word), word, combined_docs.Parent
            )

        # Go through the list of parents that have been deleted. If we find any
        # keys with parents which are a substring of the parent in this list,
        # then it means that the entire parent is deleted. We don't need verbose
        # information about the children, so we replace the parent.
        for i in range(0, len(all_deleted)):
            word = all_deleted[i]
            combined_docs.Parent = np.where(
                combined_docs["Parent"].str.startswith(word), word, combined_docs.Parent
            )

        # Create a new dataframe with only the keys which have changed
        docs_diff = combined_docs[
            combined_docs["CurrentValue"] != combined_docs["NewValue"]
        ].copy(deep=False)

        # Get the API and Version from the file name but exclude the extension.
        api_version_string = filename.split(".")[:-1]
        # Create columns `Name` and `Version` using the version string
        docs_diff["Name"] = api_version_string[0]
        docs_diff["Version"] = ".".join(api_version_string[1:])

        # These conditions are used as arguments in the `np.where` function
        # below.
        deleted_condition = docs_diff["NewValue"].isnull()
        added_condition = docs_diff["CurrentValue"].isnull()

        # Create a new `ChangeType` column. The `np.where()` function is like a
        # tenary operator. When the `deleted_condition` is `True`, the
        # `ChangeType` will be `ChangeType.Deleted`. If the added_condition is
        # `True` the `ChangeType` will be `ChangeType.Added`, otherwise the
        # `ChangeType` will be `ChangeType.Changed`.
        docs_diff["ChangeType"] = np.where(
            deleted_condition,
            ChangeType.DELETED,
            np.where(added_condition, ChangeType.ADDED, ChangeType.CHANGED),
        )

        # Filter out keys which rarely affect functionality. For example:
        # {"description", "documentation", "enum", "etag", "revision", "title",
        # "url", "rootUrl"}
        docs_diff = docs_diff[
            ~docs_diff["Key"].str.contains(
                "|".join(self._get_keys_to_ignore()), case=False
            )
        ]

        # Group keys with similar parents together and create a new column
        # called 'Count' which indicates the number of keys that have been
        # grouped together. The reason for the count column is that when keys
        # have the same parent, we group them together to improve readability.
        docs_diff_with_count = (
            docs_diff.groupby(
                ["Parent", "Added", "Deleted", "Name", "Version", "ChangeType"]
            )
            .size()
            .reset_index(name="Count")
        )

        # Add counts column
        docs_diff = docs_diff.merge(docs_diff_with_count)

        # When the count is greater than 1, update the key with the name of the
        # parent since we are consolidating keys with the same parent.
        docs_diff.loc[docs_diff["Count"] > 1, "Key"] = docs_diff["Parent"]

        return docs_diff[
            ["Key", "Added", "Deleted", "Name", "Version", "ChangeType", "Count"]
        ].drop_duplicates()

    def _build_summary_message(self, api_name, is_feature):
        """Returns a string containing the summary for a given api. The string
        returned will be in the format `fix(<api_name>): update the API`
        when `is_feature=False` and `feat(<api_name>)!: update the API`
        when `is_feature=True`.

        args:
            api_name (str): The name of the api to include in the summary.
            is_feature (bool): If True, include the prefix `feat` otherwise use
                `fix`
        """

        # Build the conventional commit string based on the arguments provided
        commit_type = "feat" if is_feature else "fix"
        return "{0}({1}): update the api".format(commit_type, api_name)

    def _get_keys_to_ignore(self):
        """Returns a list of strings with keys to ignore because they rarely
            affect functionality.

        args: None
        """
        keys_to_ignore = [
            "description",
            "documentation",
            "enum",
            "etag",
            "revision",
            "title",
            "url",
            "rootUrl",
        ]
        return keys_to_ignore

    def _get_stable_versions(self, versions):
        """Returns a pandas series `pd.Series()` of boolean values,
        corresponding to the given series, indicating whether the version is
        considered stable or not.
        args:
            versions (object): a pandas series containing version
                information for all discovery artifacts.
        """
        # Use a regex on the version to find versions with the pattern
        # <v>.<0-9>.<0-9>.<0-9> . Any api that matches this pattern will be
        # labeled as stable. In other words, v1, v1.4 and v1.4.5 is stable
        # but v1b1 v1aplha and v1beta1 is not stable.
        return versions.str.extract(r"(v\d?\.?\d?\.?\d+$)").notnull()

    def _get_summary_and_write_to_disk(self, dataframe, directory):
        """Writes summary information to file about changes made to discovery
        artifacts based on the provided dataframe and returns a dataframe
        with the same. The file `'allapis.dataframe'` is saved to the current
        working directory.
        args:
            dataframe (object): a pandas dataframe containing summary change
                information for all discovery artifacts
            directory (str): path where the summary file should be saved
        """

        dataframe["IsStable"] = self._get_stable_versions(dataframe["Version"])

        # Create a filter for features, which contains only rows which have keys
        # that have been deleted or added, that will be used as an argument in
        # the `np.where()` call below.
        filter_features = (dataframe["ChangeType"] == ChangeType.DELETED) | (
            dataframe["ChangeType"] == ChangeType.ADDED
        )

        # Create a new column `IsFeature` to indicate which rows should be
        # considered as features.
        dataframe["IsFeature"] = np.where(filter_features, True, np.nan)

        # Create a new column `IsFeatureAggregate` which will be used to
        # summarize the api changes. We can either have feature or fix but not
        # both.
        dataframe["IsFeatureAggregate"] = dataframe.groupby("Name").IsFeature.transform(
            lambda x: x.any()
        )

        # Create a new column `Summary`, which will contain a string with the
        # conventional commit message.
        dataframe["Summary"] = np.vectorize(self._build_summary_message)(
            dataframe["Name"], dataframe["IsFeatureAggregate"]
        )

        # Write the final dataframe to disk as it will be used in the
        # buildprbody.py script
        dataframe.to_csv(directory / "allapis.dataframe")
        return dataframe

    def _write_verbose_changes_to_disk(self, dataframe, directory, summary_df):
        """Writes verbose information to file about changes made to discovery
        artifacts based on the provided dataframe. A separate file is saved
        for each api in the current working directory. The extension of the
        files will be `'.verbose'`.

        args:
            dataframe (object): a pandas dataframe containing verbose change
                information for all discovery artifacts
            directory (str): path where the summary file should be saved
            summary_df (object): A dataframe containing a summary of the changes
        """
        # Array of strings which will contains verbose change information for
        # each api
        verbose_changes = []

        # Sort the dataframe to minimize file operations below.
        dataframe.sort_values(
            by=["Name", "Version", "ChangeType"], ascending=True, inplace=True
        )

        # Select only the relevant columns. We need to create verbose output
        # by Api Name, Version and ChangeType so we need to group by these
        # columns.

        change_type_groups = dataframe[
            ["Name", "Version", "ChangeType", "Key", "Count"]
        ].groupby(["Name", "Version", "ChangeType"])

        lastApi = ""
        lastVersion = ""
        lastType = ChangeType.UNKNOWN

        f = None
        for name, group in change_type_groups:
            currentApi = name[0]
            currentVersion = name[1]
            currentType = name[2]

            # We need to handing file opening and closing when processing an API
            # which is different from the previous one
            if lastApi != currentApi:
                # If we are processing a new api, close the file used for
                # processing the previous API
                if f is not None:
                    f.writelines(verbose_changes)
                    f.close()
                    f = None
                # Clear the array of strings with information from the previous
                # api and reset the last version
                verbose_changes = []
                lastVersion = ""
                # Create a file which contains verbose changes for the current
                # API being processed
                filename = "{0}.verbose".format(currentApi)
                f = open(pathlib.Path(directory / filename), "a")
                lastApi = currentApi

                # Create a filter with only the rows for the current API
                current_api_filter = summary_df["Name"] == currentApi

                # Get the string in the `Summary` column for the current api and
                # append it to `verbose_changes`. The `Summary` column contains
                # the conventional commit message. Use pandas.Series.iloc[0] to
                # retrieve only the first elemnt, since all the values in the
                # summary column are the same for a given API.
                verbose_changes.append(summary_df[current_api_filter].Summary.iloc[0])

            # If the version has changed, we need to create append a new heading
            # in the verbose summary which contains the api and version.
            if lastVersion != currentVersion:
                # Append a header string with the API and version
                verbose_changes.append(
                    "\n\n#### {0}:{1}\n\n".format(currentApi, currentVersion)
                )

                lastVersion = currentVersion
                lastType = ChangeType.UNKNOWN

            # Whenever the change type is different, we need to create a new
            # heading for the group of keys with the same change type.
            if currentType != lastType:
                if currentType == ChangeType.DELETED:
                    verbose_changes.append("\nThe following keys were deleted:\n")
                elif currentType == ChangeType.ADDED:
                    verbose_changes.append("\nThe following keys were added:\n")
                else:
                    verbose_changes.append("\nThe following keys were changed:\n")

                lastType = currentType

                # Append the keys, and corresponding count, in the same change
                # type group.
                verbose_changes.extend(
                    [
                        "- {0} (Total Keys: {1})\n".format(row["Key"], row["Count"])
                        for index, row in group[["Key", "Count"]].iterrows()
                    ]
                )

        # Make sure to close the last file and write the changes.
        if f is not None:
            f.writelines(verbose_changes)
            f.close()
            f = None

    def detect_discovery_changes(self):
        """Writes a summary of the changes to the discovery artifacts to disk
            at the path specified in `temp_dir`.

        args: None
        """
        result = pd.DataFrame()
        # Process files in parallel to improve performance
        with Pool(processes=MULTIPROCESSING_NUM_AGENTS) as pool:
            result = result.append(
                pool.map(
                    self._get_discovery_differences,
                    self._file_list,
                    MULTIPROCESSING_NUM_PER_BATCH,
                )
            )

        if len(result):
            # Sort the resulting dataframe by `Name`, `Version`, `ChangeType`
            # and `Key`
            sort_columns = ["Name", "Version", "ChangeType", "Key"]
            result.sort_values(by=sort_columns, ascending=True, inplace=True)

            # Create a folder which be used by the `createcommits.sh` and
            # `buildprbody.py` scripts.
            pathlib.Path(self._temp_dir).mkdir(exist_ok=True)

            # Create a summary which contains a conventional commit message
            # for each API and write it to disk.
            summary_df = self._get_summary_and_write_to_disk(result, self._temp_dir)

            # Create verbose change information for each API which contains
            # a list of changes by key and write it to disk.
            self._write_verbose_changes_to_disk(result, self._temp_dir, summary_df)
