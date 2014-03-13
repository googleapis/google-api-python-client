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

"""This example starts an association session.

Tags: associationsessions.start
"""

__author__ = 'jalc@google.com (Jose Alcerreca)'

import argparse
import sys

from apiclient import sample_tools
from oauth2client import client
from sample_utils import GetUniqueName

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)


def main(argv):
  # Authenticate and construct service.
  service, _ = sample_tools.init(
      argv, 'adsensehost', 'v4.1', __doc__, __file__, parents=[argparser])

  try:
    # Request a new association session.
    request = service.associationsessions().start(
        productCode='AFC',
        websiteUrl='www.example.com/blog%s' % GetUniqueName())

    result = request.execute()
    print ('Association with ID "%s" and redirect URL "%s" was started.' %
           (result['id'], result['redirectUrl']))

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
