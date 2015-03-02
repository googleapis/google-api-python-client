#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Google Inc. All Rights Reserved.
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

from shutil import copytree

import argparse
import sys


# Ignore these files and directories when copying over files into the snapshot.
IGNORE = set(['.hg', 'httplib2', 'oauth2', 'simplejson', 'static'])

# In addition to the above files also ignore these files and directories when
# copying over samples into the snapshot.
IGNORE_IN_SAMPLES = set(['googleapiclient', 'oauth2client', 'uritemplate'])

parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument('--source', default='.',
                    help='Directory name to copy from.')

parser.add_argument('--dest', default='snapshot',
                    help='Directory name to copy to.')


def _ignore(path, names):
  retval = set()
  if path != '.':
    retval = retval.union(IGNORE_IN_SAMPLES.intersection(names))
  retval = retval.union(IGNORE.intersection(names))
  return retval


def main():
  copytree(FLAGS.source, FLAGS.dest, symlinks=True,
            ignore=_ignore)


if __name__ == '__main__':
  FLAGS = parser.parse_args(sys.argv[1:])
  main()
