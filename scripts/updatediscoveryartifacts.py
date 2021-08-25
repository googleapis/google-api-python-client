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


import pathlib
import shutil
import subprocess
import tempfile

import describe
import changesummary


SCRIPTS_DIR = pathlib.Path(__file__).parent.resolve()
DISCOVERY_DOC_DIR = (
    SCRIPTS_DIR / ".." / "googleapiclient" / "discovery_cache" / "documents"
)
REFERENCE_DOC_DIR = SCRIPTS_DIR / ".." / "docs" / "dyn"
TEMP_DIR = SCRIPTS_DIR / "temp"

# Clear discovery documents and reference documents directory
shutil.rmtree(DISCOVERY_DOC_DIR, ignore_errors=True)
shutil.rmtree(REFERENCE_DOC_DIR, ignore_errors=True)

# Clear temporary directory
shutil.rmtree(TEMP_DIR, ignore_errors=True)

# Check out a fresh copy
subprocess.call(["git", "checkout", DISCOVERY_DOC_DIR])
subprocess.call(["git", "checkout", REFERENCE_DOC_DIR])

# Snapshot current discovery artifacts to a temporary directory
with tempfile.TemporaryDirectory() as current_discovery_doc_dir:
    shutil.copytree(DISCOVERY_DOC_DIR, current_discovery_doc_dir, dirs_exist_ok=True)

    # Download discovery artifacts and generate documentation
    describe.generate_all_api_documents()

    # Get a list of files changed using `git diff`
    git_diff_output = subprocess.check_output(
        [
            "git",
            "diff",
            "origin/main",
            "--name-only",
            "--",
            DISCOVERY_DOC_DIR / "*.json",
            REFERENCE_DOC_DIR / "*.html",
            REFERENCE_DOC_DIR / "*.md",
        ],
        universal_newlines=True,
    )

    # Create lists of the changed files
    all_changed_files = [
        pathlib.Path(file_name).name for file_name in git_diff_output.split("\n")
    ]
    json_changed_files = [file for file in all_changed_files if file.endswith(".json")]

    # Create temporary directory
    pathlib.Path(TEMP_DIR).mkdir()

    # Analyze the changes in discovery artifacts using the changesummary module
    changesummary.ChangeSummary(
        DISCOVERY_DOC_DIR, current_discovery_doc_dir, TEMP_DIR, json_changed_files
    ).detect_discovery_changes()

    # Write a list of the files changed to a file called `changed files` which will be used in the `createcommits.sh` script.
    with open(TEMP_DIR / "changed_files", "w") as f:
        f.writelines("\n".join(all_changed_files))
