# Copyright 2015, Google, Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import uuid

import pytest

from create_instance import main

PROJECT = os.environ['GOOGLE_CLOUD_PROJECT']
BUCKET = os.environ['CLOUD_STORAGE_BUCKET']


@pytest.mark.flaky(max_runs=3, min_passes=1)
def test_main(capsys):
    instance_name = 'test-instance-{}'.format(uuid.uuid4())
    main(
        PROJECT,
        BUCKET,
        'us-central1-f',
        instance_name,
        wait=False)

    out, _ = capsys.readouterr()

    assert "Instances in project" in out
    assert "zone us-central1-f" in out
    assert instance_name in out
    assert "Deleting instance" in out
