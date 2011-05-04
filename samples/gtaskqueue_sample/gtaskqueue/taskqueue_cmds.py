#!/usr/bin/env python
#
# Copyright (C) 2010 Google Inc.
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

"""Commands to interact with the TaskQueue object of the TaskQueue API."""


__version__ = '0.0.1'



from gtaskqueue.taskqueue_cmd_base import GoogleTaskQueueCommand

from google.apputils import appcommands
import gflags as flags

FLAGS = flags.FLAGS


class GetTaskQueueCommand(GoogleTaskQueueCommand):
    """Get properties of an existing task queue."""

    def __init__(self, name, flag_values):
        super(GetTaskQueueCommand, self).__init__(name, flag_values)
        flags.DEFINE_boolean('get_stats',
                             False,
                             'Whether to get Stats')

    def build_request(self, taskqueue_api, flag_values):
        """Build a request to get properties of a TaskQueue.

        Args:
            taskqueue_api: The handle to the taskqueue collection API.
            flag_values: The parsed command flags.
        Returns:
            The properties of the taskqueue.
        """
        return taskqueue_api.get(project=flag_values.project_name,
                                 taskqueue=flag_values.taskqueue_name,
                                 getStats=flag_values.get_stats)


def add_commands():
    appcommands.AddCmd('getqueue', GetTaskQueueCommand)
