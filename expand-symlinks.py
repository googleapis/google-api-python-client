#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
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

"""Copy files from source to dest expanding symlinks along the way.
"""

from distutils.dir_util import copy_tree

import gflags
import sys


FLAGS = gflags.FLAGS

gflags.DEFINE_string('source', '.', 'Directory name to copy from.')
gflags.DEFINE_string('dest', 'snapshot', 'Directory name to copy to.')


def main(argv):
  # Let the gflags module process the command-line arguments
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError, e:
    print '%s\\nUsage: %s ARGS\\n%s' % (e, argv[0], FLAGS)
    sys.exit(1)

  copy_tree(FLAGS.source, FLAGS.dest, verbose=True)


if __name__ == '__main__':
  main(sys.argv)
