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


"""Commands to interact with the Task object of the TaskQueue API."""


__version__ = '0.0.1'



from gtaskqueue.taskqueue_cmd_base import GoogleTaskCommand

from google.apputils import app
from google.apputils import appcommands
import gflags as flags

FLAGS = flags.FLAGS


class GetTaskCommand(GoogleTaskCommand):
    """Get properties of an existing task."""

    def __init__(self, name, flag_values):
        super(GetTaskCommand, self).__init__(name, flag_values)

    def build_request(self, task_api, flag_values):
        """Build a request to get properties of a Task.

        Args:
            task_api: The handle to the task collection API.
            flag_values: The parsed command flags.
        Returns:
            The properties of the task.
        """
        return task_api.get(project=flag_values.project_name,
                            taskqueue=flag_values.taskqueue_name,
                            task=flag_values.task_name)


class LeaseTaskCommand(GoogleTaskCommand):
    """Lease a new task from the queue."""

    def __init__(self, name, flag_values):
        super(LeaseTaskCommand, self).__init__(name,
                                               flag_values,
                                               need_task_flag=False)
        flags.DEFINE_integer('lease_secs',
                             None,
                             'The lease for the task in seconds')
        flags.DEFINE_integer('num_tasks',
                             1,
                             'The number of tasks to lease')
        flags.DEFINE_integer('payload_size_to_display',
                             2 * 1024 * 1024,
                             'Size of the payload for leased tasks to show')

    def build_request(self, task_api, flag_values):
        """Build a request to lease a pending task from the TaskQueue.

        Args:
            task_api: The handle to the task collection API.
            flag_values: The parsed command flags.
        Returns:
            A new leased task.
        """
        if not flag_values.lease_secs:
            raise app.UsageError('lease_secs must be specified')

        return task_api.lease(project=flag_values.project_name,
                              taskqueue=flag_values.taskqueue_name,
                              leaseSecs=flag_values.lease_secs,
                              numTasks=flag_values.num_tasks,
                              body={})

    def print_result(self, result):
        """Override to optionally strip the payload since it can be long."""
        if result.get('items'):
            items = []
            for task in result.get('items'):
                payloadlen = len(task['payloadBase64'])
                if payloadlen > FLAGS.payload_size_to_display:
                    extra = payloadlen - FLAGS.payload_size_to_display
                    task['payloadBase64'] = ('%s(%d more bytes)' %
                        (task['payloadBase64'][:FLAGS.payload_size_to_display],
                         extra))
                items.append(task)
            result['items'] = items
        GoogleTaskCommand.print_result(self, result)


class DeleteTaskCommand(GoogleTaskCommand):
    """Delete an existing task."""

    def __init__(self, name, flag_values):
        super(DeleteTaskCommand, self).__init__(name, flag_values)

    def build_request(self, task_api, flag_values):
        """Build a request to delete a Task.

        Args:
            task_api: The handle to the taskqueue collection API.
            flag_values: The parsed command flags.
        Returns:
            Whether the delete was successful.
        """
        return task_api.delete(project=flag_values.project_name,
                               taskqueue=flag_values.taskqueue_name,
                               task=flag_values.task_name)


class ListTasksCommand(GoogleTaskCommand):
    """Lists all tasks in a queue (currently upto a max of 100)."""

    def __init__(self, name, flag_values):
        super(ListTasksCommand, self).__init__(name,
                                               flag_values,
                                               need_task_flag=False)

    def build_request(self, task_api, flag_values):
        """Build a request to lists tasks in a queue.

        Args:
            task_api: The handle to the taskqueue collection API.
            flag_values: The parsed command flags.
        Returns:
          A list of pending tasks in the queue.
        """
        return task_api.list(project=flag_values.project_name,
                             taskqueue=flag_values.taskqueue_name)


def add_commands():
    appcommands.AddCmd('listtasks', ListTasksCommand)
    appcommands.AddCmd('gettask', GetTaskCommand)
    appcommands.AddCmd('deletetask', DeleteTaskCommand)
    appcommands.AddCmd('leasetask', LeaseTaskCommand)
