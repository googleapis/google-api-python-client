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

from apiclient.errors import BatchError
from apiclient.http import BatchHttpRequest
from apiclient.http import HttpMockSequence
from apiclient.http import HttpRequest
from apiclient.http import MediaFileUpload
from apiclient.http import MediaUpload
from apiclient.http import set_user_agent
from apiclient.model import JsonModel


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
    self.assertEquals(new_req.multipart_boundary, '---flubber--')

EXPECTED = """POST /someapi/v1/collection/?foo=bar HTTP/1.1
Content-Type: application/json
MIME-Version: 1.0
Host: www.googleapis.com
content-length: 2\r\n\r\n{}"""


NO_BODY_EXPECTED = """POST /someapi/v1/collection/?foo=bar HTTP/1.1
Content-Type: application/json
MIME-Version: 1.0
Host: www.googleapis.com
content-length: 0\r\n\r\n"""


RESPONSE = """HTTP/1.1 200 OK
Content-Type application/json
Content-Length: 14
ETag: "etag/pony"\r\n\r\n{"answer": 42}"""


BATCH_RESPONSE = """--batch_foobarbaz
Content-Type: application/http
Content-Transfer-Encoding: binary
Content-ID: <randomness+1>

HTTP/1.1 200 OK
Content-Type application/json
Content-Length: 14
ETag: "etag/pony"\r\n\r\n{"foo": 42}

--batch_foobarbaz
Content-Type: application/http
Content-Transfer-Encoding: binary
Content-ID: <randomness+2>

HTTP/1.1 200 OK
Content-Type application/json
Content-Length: 14
ETag: "etag/sheep"\r\n\r\n{"baz": "qux"}
--batch_foobarbaz--"""


class TestBatch(unittest.TestCase):

  def setUp(self):
    model = JsonModel()
    self.request1 = HttpRequest(
        None,
        model.response,
        'https://www.googleapis.com/someapi/v1/collection/?foo=bar',
        method='POST',
        body='{}',
        headers={'content-type': 'application/json'})

    self.request2 = HttpRequest(
        None,
        model.response,
        'https://www.googleapis.com/someapi/v1/collection/?foo=bar',
        method='GET',
        body='',
        headers={'content-type': 'application/json'})


  def test_id_to_from_content_id_header(self):
    batch = BatchHttpRequest()
    self.assertEquals('12', batch._header_to_id(batch._id_to_header('12')))

  def test_invalid_content_id_header(self):
    batch = BatchHttpRequest()
    self.assertRaises(BatchError, batch._header_to_id, '[foo+x]')
    self.assertRaises(BatchError, batch._header_to_id, 'foo+1')
    self.assertRaises(BatchError, batch._header_to_id, '<foo>')

  def test_serialize_request(self):
    batch = BatchHttpRequest()
    request = HttpRequest(
        None,
        None,
        'https://www.googleapis.com/someapi/v1/collection/?foo=bar',
        method='POST',
        body='{}',
        headers={'content-type': 'application/json'},
        methodId=None,
        resumable=None)
    s = batch._serialize_request(request).splitlines()
    self.assertEquals(s, EXPECTED.splitlines())

  def test_serialize_request_media_body(self):
    batch = BatchHttpRequest()
    f = open(datafile('small.png'))
    body = f.read()
    f.close()

    request = HttpRequest(
        None,
        None,
        'https://www.googleapis.com/someapi/v1/collection/?foo=bar',
        method='POST',
        body=body,
        headers={'content-type': 'application/json'},
        methodId=None,
        resumable=None)
    s = batch._serialize_request(request).splitlines()


  def test_serialize_request_no_body(self):
    batch = BatchHttpRequest()
    request = HttpRequest(
        None,
        None,
        'https://www.googleapis.com/someapi/v1/collection/?foo=bar',
        method='POST',
        body='',
        headers={'content-type': 'application/json'},
        methodId=None,
        resumable=None)
    s = batch._serialize_request(request).splitlines()
    self.assertEquals(s, NO_BODY_EXPECTED.splitlines())

  def test_deserialize_response(self):
    batch = BatchHttpRequest()
    resp, content = batch._deserialize_response(RESPONSE)

    self.assertEquals(resp.status, 200)
    self.assertEquals(resp.reason, 'OK')
    self.assertEquals(resp.version, 11)
    self.assertEquals(content, '{"answer": 42}')

  def test_new_id(self):
    batch = BatchHttpRequest()

    id_ = batch._new_id()
    self.assertEquals(id_, '1')

    id_ = batch._new_id()
    self.assertEquals(id_, '2')

    batch.add(self.request1, request_id='3')

    id_ = batch._new_id()
    self.assertEquals(id_, '4')

  def test_add(self):
    batch = BatchHttpRequest()
    batch.add(self.request1, request_id='1')
    self.assertRaises(KeyError, batch.add, self.request1, request_id='1')

  def test_add_fail_for_resumable(self):
    batch = BatchHttpRequest()

    upload = MediaFileUpload(
        datafile('small.png'), chunksize=500, resumable=True)
    self.request1.resumable = upload
    self.assertRaises(BatchError, batch.add, self.request1, request_id='1')

  def test_execute(self):
    class Callbacks(object):
      def __init__(self):
        self.responses = {}

      def f(self, request_id, response):
        self.responses[request_id] = response

    batch = BatchHttpRequest()
    callbacks = Callbacks()

    batch.add(self.request1, callback=callbacks.f)
    batch.add(self.request2, callback=callbacks.f)
    http = HttpMockSequence([
      ({'status': '200',
        'content-type': 'multipart/mixed; boundary="batch_foobarbaz"'},
       BATCH_RESPONSE),
      ])
    batch.execute(http)
    self.assertEqual(callbacks.responses['1'], {'foo': 42})
    self.assertEqual(callbacks.responses['2'], {'baz': 'qux'})

  def test_execute_request_body(self):
    batch = BatchHttpRequest()

    batch.add(self.request1)
    batch.add(self.request2)
    http = HttpMockSequence([
      ({'status': '200',
        'content-type': 'multipart/mixed; boundary="batch_foobarbaz"'},
        'echo_request_body'),
      ])
    try:
      batch.execute(http)
      self.fail('Should raise exception')
    except BatchError, e:
      boundary, _ = e.content.split(None, 1)
      self.assertEqual('--', boundary[:2])
      parts = e.content.split(boundary)
      self.assertEqual(4, len(parts))
      self.assertEqual('', parts[0])
      self.assertEqual('--', parts[3])
      header = parts[1].splitlines()[1]
      self.assertEqual('Content-Type: application/http', header)

  def test_execute_global_callback(self):
    class Callbacks(object):
      def __init__(self):
        self.responses = {}

      def f(self, request_id, response):
        self.responses[request_id] = response

    callbacks = Callbacks()
    batch = BatchHttpRequest(callback=callbacks.f)

    batch.add(self.request1)
    batch.add(self.request2)
    http = HttpMockSequence([
      ({'status': '200',
        'content-type': 'multipart/mixed; boundary="batch_foobarbaz"'},
       BATCH_RESPONSE),
      ])
    batch.execute(http)
    self.assertEqual(callbacks.responses['1'], {'foo': 42})
    self.assertEqual(callbacks.responses['2'], {'baz': 'qux'})

if __name__ == '__main__':
  unittest.main()
