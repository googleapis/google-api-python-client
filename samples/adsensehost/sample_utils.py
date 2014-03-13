#!/usr/bin/python
#
# Copyright 2012 Google Inc. All Rights Reserved.
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

"""Auxiliary file for AdSense Host API code samples."""

__author__ = 'jalc@google.com (Jose Alcerreca)'

import datetime


def GetUniqueName(max_len=None):
  """Returns a unique value to append to various properties in the samples.

  Shamelessly stolen from http://code.google.com/p/google-api-ads-python.

  Args:
    max_len: int Maximum length for the unique name.

  Returns:
    str Unique name.
  """
  dt = datetime.datetime.now()
  name = '%s%s%s%s%s%s%s' % (dt.microsecond, dt.second, dt.minute, dt.hour,
                             dt.day, dt.month, dt.year)
  if max_len > len(name):
    max_len = len(name)
  return name[:max_len]
