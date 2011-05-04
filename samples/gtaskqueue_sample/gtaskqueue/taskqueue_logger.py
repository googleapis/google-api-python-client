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

"""Log settings for taskqueue_puller module."""



import logging
import logging.config
from google.apputils import app
import gflags as flags

FLAGS = flags.FLAGS
flags.DEFINE_string(
        'log_output_file',
        '/tmp/taskqueue-puller.log',
        'Logfile name for taskqueue_puller.')


logger = logging.getLogger('TaskQueueClient')


def set_logger():
    """Settings for taskqueue_puller logger."""
    logger.setLevel(logging.INFO)

    # create formatter
    formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Set size of the log file and the backup count  for rotated log files.
    handler = logging.handlers.RotatingFileHandler(FLAGS.log_output_file,
                                                   maxBytes = 1024 * 1024,
                                                   backupCount = 5)
    # add formatter to handler
    handler.setFormatter(formatter)
    # add formatter to handler
    logger.addHandler(handler)

if __name__ == '__main__':
    app.run()
