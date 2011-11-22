#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc.
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

"""Http tests

Unit tests for the apiclient.http.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

# Do not remove the httplib2 import
import httplib2
import os
import unittest

from apiclient.http import set_user_agent
from apiclient.http import HttpMockSequence
from apiclient.http import HttpRequest
from apiclient.http import MediaUpload
from apiclient.http import MediaFileUpload


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


def datafile(filename):
  return os.path.join(DATA_DIR, filename)

class TestUserAgent(unittest.TestCase):

  def test_set_user_agent(self):
    http = HttpMockSequence([
      ({'status': '200'}, 'echo_request_headers'),
      ])

    http = set_user_agent(http, "my_app/5.5")
    resp, content = http.request("http://example.com")
    self.assertEqual(content['user-agent'], 'my_app/5.5')

  def test_set_user_agent_nested(self):
    http = HttpMockSequence([
      ({'status': '200'}, 'echo_request_headers'),
      ])

    http = set_user_agent(http, "my_app/5.5")
    http = set_user_agent(http, "my_library/0.1")
    resp, content = http.request("http://example.com")
    self.assertEqual(content['user-agent'], 'my_app/5.5 my_library/0.1')

  def test_media_file_upload_to_from_json(self):
    upload = MediaFileUpload(
        datafile('small.png'), chunksize=500, resumable=True)
    self.assertEquals('image/png', upload.mimetype())
    self.assertEquals(190, upload.size())
    self.assertEquals(True, upload.resumable())
    self.assertEquals(500, upload.chunksize())
    self.assertEquals('PNG', upload.getbytes(1, 3))

    json = upload.to_json()
    new_upload = MediaUpload.new_from_json(json)

    self.assertEquals('image/png', new_upload.mimetype())
    self.assertEquals(190, new_upload.size())
    self.assertEquals(True, new_upload.resumable())
    self.assertEquals(500, new_upload.chunksize())
    self.assertEquals('PNG', new_upload.getbytes(1, 3))

  def test_http_request_to_from_json(self):

    def _postproc(*kwargs):
      pass

    http = httplib2.Http()
    media_upload = MediaFileUpload(
        datafile('small.png'), chunksize=500, resumable=True)
    req = HttpRequest(
        http,
        _postproc,
        'http://example.com',
        method='POST',
        body='{}',
        headers={'content-type': 'multipart/related; boundary="---flubber"'},
        methodId='foo',
        resumable=media_upload)

    json = req.to_json()
    new_req = HttpRequest.from_json(json, http, _postproc)

    self.assertEquals(new_req.headers, 
                      {'content-type':
                       'multipart/related; boundary="---flubber"'})
    self.assertEquals(new_req.uri, 'http://example.com')
    self.assertEquals(new_req.body, '{}')
    self.assertEquals(new_req.http, http)
    self.assertEquals(new_req.resumable.to_json(), media_upload.to_json())
    self.assertEquals(new_req.multipart_boundary, '---flubber')


if __name__ == '__main__':
  unittest.main()
