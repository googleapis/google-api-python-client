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
import os
import pandas as pd


class ChangeType(IntEnum):
    UNKNOWN = 0
    DELETED = 1
    ADDED = 2
    CHANGED = 3


def get_commit_link(name):
    """Return a string with a link to the last commit for the given
        API Name.
    args:
        name (str): The name of the api.
    """

    url = "https://github.com/googleapis/google-api-python-client/commit/"
    sha = None
    api_link = ""

    file_path = os.path.join(directory, "{0}.sha".format(name))
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            sha = f.readline().rstrip()
            if sha:
                api_link = "[{0}]({1}{2})".format(" [More details]", url, sha)

    return api_link


if __name__ == "__main__":
    directory = "temp"
    dataframe = pd.read_csv("temp/allapis.dataframe")
    dataframe["Version"] = dataframe["Version"].astype(str)

    dataframe["Commit"] = np.vectorize(get_commit_link)(dataframe["Name"])

    stable_and_breaking = (
        dataframe[
            dataframe["IsStable"]
            & (dataframe["ChangeType"] == ChangeType.DELETED)
        ][["Name", "Version", "Commit"]]
        .drop_duplicates()
        .agg("".join, axis=1)
        .values
    )

    prestable_and_breaking = (
        dataframe[
            (dataframe["IsStable"] == False)
            & (dataframe["ChangeType"] == ChangeType.DELETED)
        ][["Name", "Version", "Commit"]]
        .drop_duplicates()
        .agg("".join, axis=1)
        .values
    )

    all_apis = (
        dataframe[["Name", "Version", "Commit"]]
        .drop_duplicates()
        .agg("".join, axis=1)
        .values
    )

    with open(os.path.join(directory, "allapis.summary"), "w") as f:
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
                ["## Discovery Artifact Change Summary:\n", "\n".join(all_apis), "\n"]
            )
