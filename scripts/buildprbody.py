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
import numpy as np
import pandas as pd
import pathlib

from changesummary import ChangeType

SCRIPTS_DIR = pathlib.Path(__file__).parent.resolve()
CHANGE_SUMMARY_DIR = SCRIPTS_DIR / "temp"


class BuildPrBody:
    """Represents the PR body which contains the change summary between 2
    directories containing artifacts.
    """

    def __init__(self, change_summary_directory):
        """Initializes an instance of a BuildPrBody.

        Args:
            change_summary_directory (str): The relative path to the directory
            which contains the change summary output.
        """
        self._change_summary_directory = change_summary_directory

    def get_commit_uri(self, name):
        """Return a uri to the last commit for the given API Name.

        Args:
            name (str): The name of the api.
        """

        url = "https://github.com/googleapis/google-api-python-client/commit/"
        sha = None
        api_link = ""

        file_path = pathlib.Path(self._change_summary_directory) / "{0}.sha".format(name)
        if file_path.is_file():
            with open(file_path, "r") as f:
                sha = f.readline().rstrip()
                if sha:
                    api_link = "{0}{1}".format(url, sha)

        return api_link

    def generate_pr_body(self):
        """
        Generates a PR body given an input file `'allapis.dataframe'` and
        writes it to disk with file name `'allapis.summary'`.
        """
        directory = pathlib.Path(self._change_summary_directory)
        dataframe = pd.read_csv(directory / "allapis.dataframe")
        dataframe["Version"] = dataframe["Version"].astype(str)

        dataframe["Commit"] = np.vectorize(self.get_commit_uri)(dataframe["Name"])

        stable_and_breaking = (
            dataframe[
                dataframe["IsStable"] & (dataframe["ChangeType"] == ChangeType.DELETED)
            ][["Name", "Version", "Commit"]]
            .drop_duplicates()
            .agg(" ".join, axis=1)
            .values
        )

        prestable_and_breaking = (
            dataframe[
                (dataframe["IsStable"] == False)
                & (dataframe["ChangeType"] == ChangeType.DELETED)
            ][["Name", "Version", "Commit"]]
            .drop_duplicates()
            .agg(" ".join, axis=1)
            .values
        )

        all_apis = (
            dataframe[["Summary", "Commit"]]
            .drop_duplicates()
            .agg(" ".join, axis=1)
            .values
        )

        with open(directory / "allapis.summary", "w") as f:
            if len(stable_and_breaking) > 0:
                f.writelines(
                    [
                        "## Deleted keys were detected in the following stable discovery artifacts:\n",
                        "\n".join(stable_and_breaking),
                        "\n\n",
                    ]
                )

            if len(prestable_and_breaking) > 0:
                f.writelines(
                    [
                        "## Deleted keys were detected in the following pre-stable discovery artifacts:\n",
                        "\n".join(prestable_and_breaking),
                        "\n\n",
                    ]
                )

            if len(all_apis) > 0:
                f.writelines(
                    [
                        "## Discovery Artifact Change Summary:\n",
                        "\n".join(all_apis),
                        "\n",
                    ]
                )


if __name__ == "__main__":
    BuildPrBody(CHANGE_SUMMARY_DIR).generate_pr_body()
