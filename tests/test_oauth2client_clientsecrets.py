# Copyright 2011 Google Inc.
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

"""Unit tests for oauth2client.clientsecrets."""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'


import os
import unittest
import StringIO

import httplib2

from oauth2client import clientsecrets


class OAuth2CredentialsTests(unittest.TestCase):

  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_validate_error(self):
    ERRORS = [
      ('{}', 'Invalid'),
      ('{"foo": {}}', 'Unknown'),
      ('{"web": {}}', 'Missing'),
      ('{"web": {"client_id": "dkkd"}}', 'Missing'),
      ("""{
         "web": {
           "client_id": "[[CLIENT ID REQUIRED]]",
           "client_secret": "[[CLIENT SECRET REQUIRED]]",
           "redirect_uris": ["http://localhost:8080/oauth2callback"],
           "auth_uri": "",
           "token_uri": ""
         }
       }
       """, 'Property'),
      ]
    for src, match in ERRORS:
      # Test load(s)
      try:
        clientsecrets.loads(src)
        self.fail(src + ' should not be a valid client_secrets file.')
      except clientsecrets.InvalidClientSecretsError, e:
        self.assertTrue(str(e).startswith(match))

      # Test loads(fp)
      try:
        fp = StringIO.StringIO(src)
        clientsecrets.load(fp)
        self.fail(src + ' should not be a valid client_secrets file.')
      except clientsecrets.InvalidClientSecretsError, e:
        self.assertTrue(str(e).startswith(match))

  def test_load_by_filename(self):
    try:
      clientsecrets.loadfile(os.path.join(__file__, '..',
                             'afilethatisntthere.json'))
      self.fail('should fail to load a missing client_secrets file.')
    except clientsecrets.InvalidClientSecretsError, e:
      self.assertTrue(str(e).startswith('File'))


if __name__ == '__main__':
  unittest.main()
