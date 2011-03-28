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

"""Utility functions for setup.py file(s)."""


__author__ = 'tom.h.miller@gmail.com (Tom Miller)'

import sys


def is_missing(packages):
  """Return True if a package can't be imported."""

  retval = True
  sys_path_original = sys.path[:]
  # Remove the current directory from the list of paths to check when
  # importing modules.
  try:
    # Sometimes it's represented by an empty string?
    sys.path.remove('')
  except ValueError:
    import os.path
    try:
      sys.path.remove(os.path.abspath(os.path.curdir))
    except ValueError:
      pass
  if not isinstance(packages, type([])):
    packages = [packages]
  for name in packages:
    try:
      __import__(name)
      retval = False
    except ImportError:
      retval = True
    if retval == False:
      break

  sys.path = sys_path_original

  return retval
