#!/usr/bin/env python
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

"""Class to encapsulate task related information and methods on task_puller."""



import base64
import oauth2 as oauth
import os
import subprocess
import tempfile
import time
import urllib2
from apiclient.errors import HttpError
from gtaskqueue.taskqueue_logger import logger
import gflags as flags


FLAGS = flags.FLAGS
flags.DEFINE_string(
        'executable_binary',
        '/bin/cat',
        'path of the binary to be executed')
flags.DEFINE_string(
        'output_url',
        '',
        'url to which output is posted. The url must include param name, '
        'value for which is populated with task_id from puller while posting '
        'the data. Format of output url is absolute url which handles the'
        'post request from task queue puller.'
        '(Eg: "http://taskpuller.appspot.com/taskdata?name=").'
        'The Param value is always the task_id. The handler for this post'
        'should be able to associate the task with its id and take'
        'appropriate action. Use the appengine_access_token.py tool to'
        'generate the token and store it in a file before you start.')
flags.DEFINE_string(
        'appengine_access_token_file',
        None,
        'File containing an Appengine Access token, if any. If present this'
        'token is added to the output_url request, so that the output_url can'
        'be an authenticated end-point. Use the appengine_access_token.py tool'
        'to generate the token and store it in a file before you start.')
flags.DEFINE_float(
        'task_timeout_secs',
        '3600',
        'timeout to kill the task')


class ClientTaskInitError(Exception):
    """Raised when initialization of client task fails."""

    def __init__(self, task_id, error_str):
        Exception.__init__(self)
        self.task_id = task_id
        self.error_str = error_str

    def __str__(self):
        return ('Error initializing task "%s". Error details "%s". '
                        % (self.task_id, self.error_str))


class ClientTask(object):
    """Class to encapsulate task information pulled by taskqueue_puller module.

    This class is responsible for creating an independent client task object by
    taking some information from lease response task object. It encapsulates
    methods responsible for spawning an independent subprocess for executing
    the task, tracking the status of the task and also deleting the task from
    taskqeueue when completed. It also has the functionality to give the output
    back to the application by posting to the specified url.
    """

    def __init__(self, task):
        self._task = task
        self._process = None
        self._output_file = None

    # Class method that caches the Appengine Access Token if any
    @classmethod
    def get_access_token(cls):
        if not FLAGS.appengine_access_token_file:
            return None
        if not _access_token:
            fhandle = open(FLAGS.appengine_access_token_file, 'rb')
            _access_token = oauth.Token.from_string(fhandle.read())
            fhandle.close()
        return _access_token

    def init(self):
        """Extracts information from task object and intializes processing.

        Extracts id and payload from task object, decodes the payload and puts
        it in input file. After this, it spawns a subprocess to execute the
        task.

        Returns:
            True if everything till task execution starts fine.
            False if anything goes wrong in initialization of task execution.
        """
        try:
            self.task_id = self._task.get('id')
            self._payload = self._decode_base64_payload(
                self._task.get('payloadBase64'))
            self._payload_file = self._dump_payload_to_file()
            self._start_task_execution()
            return True
        except ClientTaskInitError, ctie:
            logger.error(str(ctie))
            return False

    def _decode_base64_payload(self, encoded_str):
        """Method to decode payload encoded in base64."""
        try:
            # If the payload is empty, do not try to decode it. Payload usually
            # not expected to be empty and hence log a warning and then
            # continue.
            if encoded_str:
                decoded_str = base64.urlsafe_b64decode(
                    encoded_str.encode('utf-8'))
                return decoded_str
            else:
                logger.warn('Empty paylaod for task %s' % self.task_id)
                return ''
        except base64.binascii.Error, berror:
            logger.error('Error decoding payload for task %s. Error details %s'
                         % (self.task_id, str(berror)))
            raise ClientTaskInitError(self.task_id, 'Error decoding payload')
        # Generic catch block to avoid crashing of puller due to some bad
        # encoding issue wih payload of any task.
        except:
            raise ClientTaskInitError(self.task_id, 'Error decoding payload')

    def _dump_payload_to_file(self):
        """Method to write input extracted from payload to a temporary file."""
        try:
            (fd, fname) = tempfile.mkstemp()
            f = os.fdopen(fd, 'w')
            f.write(self._payload)
            f.close()
            return fname
        except OSError:
            logger.error('Error dumping payload %s. Error details %s' %
                                      (self.task_id, str(OSError)))
            raise ClientTaskInitError(self.task_id, 'Error dumping payload')

    def _get_input_file(self):
        return self._payload_file

    def _post_output(self):
        """Posts the outback back to specified url in the form of a byte
        array.

        It reads the output generated by the task as a byte-array. It posts the
        response to specified url appended with the taskId. The  application
        using the taskqueue must have a handler to handle the data being posted
        from puller. Format of body of response object is byte-array to make
        the it genric for any kind of output generated.

        Returns:
            True/False based on post status.
        """
        if FLAGS.output_url:
            try:
                f = open(self._get_output_file(), 'rb')
                body = f.read()
                f.close()
                url = FLAGS.output_url + self.task_id
                logger.debug('Posting data to url %s' % url)
                headers = {'Content-Type': 'byte-array'}
                # Add an access token to the headers if specified.
                # This enables the output_url to be authenticated and not open.
                access_token = ClientTask.get_access_token()
                if access_token:
                    consumer = oauth.Consumer('anonymous', 'anonymous')
                    oauth_req = oauth.Request.from_consumer_and_token(
                        consumer,
                        token=access_token,
                        http_url=url)
                    headers.update(oauth_req.to_header())
                # TODO: Use httplib instead of urllib for consistency.
                req = urllib2.Request(url, body, headers)
                urllib2.urlopen(req)
            except ValueError:
                logger.error('Error posting data back %s. Error details %s'
                             % (self.task_id, str(ValueError)))
                return False
            except Exception:
                logger.error('Exception while posting data back %s. Error'
                             'details %s' % (self.task_id, str(Exception)))
                return False
        return True

    def _get_output_file(self):
        """Returns the output file if it exists, else creates it and returns
        it."""
        if not self._output_file:
            (_, self._output_file) = tempfile.mkstemp()
        return self._output_file

    def get_task_id(self):
        return self.task_id

    def _start_task_execution(self):
        """Method to spawn subprocess to execute the tasks.

        This method splits the commands/executable_binary to desired arguments
        format for Popen API. It appends input and output files to the
        arguments. It is assumed that commands/executable_binary expects input
        and output files as first and second positional parameters
        respectively.
        """
        # TODO: Add code to handle the cleanly shutdown when a process is killed
        # by Ctrl+C.
        try:
            cmdline = FLAGS.executable_binary.split(' ')
            cmdline.append(self._get_input_file())
            cmdline.append(self._get_output_file())
            self._process = subprocess.Popen(cmdline)
            self.task_start_time = time.time()
        except OSError:
            logger.error('Error creating subprocess %s. Error details %s'
                        % (self.task_id, str(OSError)))
            self._cleanup()
            raise ClientTaskInitError(self.task_id,
                                      'Error creating subprocess')
        except ValueError:
            logger.error('Invalid arguments while executing task ',
                         self.task_id)
            self._cleanup()
            raise ClientTaskInitError(self.task_id,
                                      'Invalid arguments while executing task')

    def is_completed(self, task_api):
        """Method to check if task has finished executing.

        This is responsible for checking status of task execution. If the task
        has already finished executing, it deletes the task from the task
        queue. If the task has been running since long time then it assumes
        that there is high proabbility that it is dfunct and hence kills the
        corresponding subprocess. In this case, task had not completed
        successfully and hence we do not delete it form the taskqueue. In above
        two cases, task completion status is returned as true since there is
        nothing more to run in the task. In all other cases, task is still
        running and hence we return false as completion status.

        Args:
            task_api: handle for taskqueue api collection.

        Returns:
            Task completion status (True/False)
        """
        status = False
        try:
            task_status = self._process.poll()
            if task_status == 0:
                status = True
                if self._post_output():
                    self._delete_task_from_queue(task_api)
                self._cleanup()
            elif self._has_timedout():
                status = True
                self._kill_subprocess()
        except OSError:
            logger.error('Error during polling status of task %s, Error ' 
                         'details %s' % (self.task_id, str(OSError)))
        return status

    def _cleanup(self):
        """Cleans up temporary input/output files used in task execution."""
        try:
            if os.path.exists(self._get_input_file()):
                os.remove(self._get_input_file())
            if os.path.exists(self._get_output_file()):
                os.remove(self._get_output_file())
        except OSError:
            logger.error('Error during file cleanup for task %s. Error'
                         'details %s' % (self.task_id, str(OSError)))

    def _delete_task_from_queue(self, task_api):
        """Method to delete the task from the taskqueue.

        First, it tries to post the output back to speified url. On successful
        post, the task is deleted from taskqueue since the task has produced
        expected output. If the post was unsuccessful, the task is not deleted
        form the tskqueue since the expected output has yet not reached the
        application. In either case cleanup is performed on the task.

        Args:
            task_api: handle for taskqueue api collection.

        Returns:
            Delete status (True/False)
        """

        try:
            delete_request = task_api.tasks().delete(
                project=FLAGS.project_name,
                taskqueue=FLAGS.taskqueue_name,
                task=self.task_id)
            delete_request.execute()
        except HttpError, http_error:
            logger.error('Error deleting task %s from taskqueue.'
                         'Error details %s'
                         % (self.task_id, str(http_error)))

    def _has_timedout(self):
        """Checks if task has been running since long and has timedout."""
        if (time.time() - self.task_start_time) > FLAGS.task_timeout_secs:
            return True
        else:
            return False

    def _kill_subprocess(self):
        """Kills the process after cleaning up the task."""
        self._cleanup()
        try:
            self._process.kill()
            logger.info('Trying to kill task %s, since it has been running '
                        'for long' % self.task_id)
        except OSError:
            logger.error('Error killing task %s. Error details %s'
                         % (self.task_id, str(OSError)))
