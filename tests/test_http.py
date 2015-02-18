#!/usr/bin/python2.4
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

"""Http tests

Unit tests for the googleapiclient.http.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'

# Do not remove the httplib2 import
import httplib2
import logging
import os
import unittest
import random
import time


from six import BytesIO, StringIO
from io import FileIO
from six.moves.urllib.parse import urlencode

from googleapiclient.discovery import build
from googleapiclient.errors import BatchError
from googleapiclient.errors import HttpError
from googleapiclient.errors import InvalidChunkSizeError
from googleapiclient.http import BatchHttpRequest
from googleapiclient.http import HttpMock
from googleapiclient.http import HttpMockSequence
from googleapiclient.http import HttpRequest
from googleapiclient.http import MAX_URI_LENGTH
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaInMemoryUpload
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.http import MediaUpload
from googleapiclient.http import _StreamSlice
from googleapiclient.http import set_user_agent
from googleapiclient.model import JsonModel
from oauth2client.client import Credentials


class MockCredentials(Credentials):
  """Mock class for all Credentials objects."""
  def __init__(self, bearer_token):
    super(MockCredentials, self).__init__()
    self._authorized = 0
    self._refreshed = 0
    self._applied = 0
    self._bearer_token = bearer_token

  def authorize(self, http):
    self._authorized += 1

    request_orig = http.request

    # The closure that will replace 'httplib2.Http.request'.
    def new_request(uri, method='GET', body=None, headers=None,
                    redirections=httplib2.DEFAULT_MAX_REDIRECTS,
                    connection_type=None):
      # Modify the request headers to add the appropriate
      # Authorization header.
      if headers is None:
        headers = {}
      self.apply(headers)

      resp, content = request_orig(uri, method, body, headers,
                                   redirections, connection_type)

      return resp, content

    # Replace the request method with our own closure.
    http.request = new_request

    # Set credentials as a property of the request method.
    setattr(http.request, 'credentials', self)

    return http

  def refresh(self, http):
    self._refreshed += 1

  def apply(self, headers):
    self._applied += 1
    headers['authorization'] = self._bearer_token + ' ' + str(self._refreshed)


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


def datafile(filename):
  return os.path.join(DATA_DIR, filename)


class TestUserAgent(unittest.TestCase):

  def test_set_user_agent(self):
    http = HttpMockSequence([({'status': '200'}, 'echo_request_headers'), ])

    http = set_user_agent(http, "my_app/5.5")
    resp, content = http.request("http://example.com")
    self.assertEqual('my_app/5.5', content['user-agent'])

  def test_set_user_agent_nested(self):
    http = HttpMockSequence([({'status': '200'}, 'echo_request_headers'), ])

    http = set_user_agent(http, "my_app/5.5")
    http = set_user_agent(http, "my_library/0.1")
    resp, content = http.request("http://example.com")
    self.assertEqual('my_app/5.5 my_library/0.1', content['user-agent'])


class TestMediaUpload(unittest.TestCase):

  def test_media_file_upload_to_from_json(self):
    upload = MediaFileUpload(
        datafile('small.png'), chunksize=500, resumable=True)
    self.assertEqual('image/png', upload.mimetype())
    self.assertEqual(190, upload.size())
    self.assertEqual(True, upload.resumable())
    self.assertEqual(500, upload.chunksize())
    self.assertEqual(b'PNG', upload.getbytes(1, 3))

    json = upload.to_json()
    new_upload = MediaUpload.new_from_json(json)

    self.assertEqual('image/png', new_upload.mimetype())
    self.assertEqual(190, new_upload.size())
    self.assertEqual(True, new_upload.resumable())
    self.assertEqual(500, new_upload.chunksize())
    self.assertEqual(b'PNG', new_upload.getbytes(1, 3))

  def test_media_file_upload_raises_on_invalid_chunksize(self):
    self.assertRaises(InvalidChunkSizeError, MediaFileUpload,
                      datafile('small.png'), mimetype='image/png',
                      chunksize=-2, resumable=True)

  def test_media_inmemory_upload(self):
    media = MediaInMemoryUpload(b'abcdef', mimetype='text/plain', chunksize=10,
                                resumable=True)
    self.assertEqual('text/plain', media.mimetype())
    self.assertEqual(10, media.chunksize())
    self.assertTrue(media.resumable())
    self.assertEqual(b'bc', media.getbytes(1, 2))
    self.assertEqual(6, media.size())

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

    self.assertEqual({'content-type':
                      'multipart/related; boundary="---flubber"'},
                     new_req.headers)
    self.assertEqual('http://example.com', new_req.uri)
    self.assertEqual('{}', new_req.body)
    self.assertEqual(http, new_req.http)
    self.assertEqual(media_upload.to_json(), new_req.resumable.to_json())

    self.assertEqual(random.random, new_req._rand)
    self.assertEqual(time.sleep, new_req._sleep)


class TestMediaIoBaseUpload(unittest.TestCase):

  def test_media_io_base_upload_from_file_io(self):
    fd = FileIO(datafile('small.png'), 'r')
    upload = MediaIoBaseUpload(
        fd=fd, mimetype='image/png', chunksize=500, resumable=True)
    self.assertEqual('image/png', upload.mimetype())
    self.assertEqual(190, upload.size())
    self.assertEqual(True, upload.resumable())
    self.assertEqual(500, upload.chunksize())
    self.assertEqual(b'PNG', upload.getbytes(1, 3))

  def test_media_io_base_upload_from_file_object(self):
    f = open(datafile('small.png'), 'rb')
    upload = MediaIoBaseUpload(
        fd=f, mimetype='image/png', chunksize=500, resumable=True)
    self.assertEqual('image/png', upload.mimetype())
    self.assertEqual(190, upload.size())
    self.assertEqual(True, upload.resumable())
    self.assertEqual(500, upload.chunksize())
    self.assertEqual(b'PNG', upload.getbytes(1, 3))
    f.close()

  def test_media_io_base_upload_serializable(self):
    f = open(datafile('small.png'), 'rb')
    upload = MediaIoBaseUpload(fd=f, mimetype='image/png')

    try:
      json = upload.to_json()
      self.fail('MediaIoBaseUpload should not be serializable.')
    except NotImplementedError:
      pass

  # def test_media_io_base_upload_from_string_io(self):
  #   f = open(datafile('small.png'), 'r')
  #   fd = StringIO(f.read().encode())
  #   f.close()
  #
  #   upload = MediaIoBaseUpload(
  #       fd=fd, mimetype='image/png', chunksize=500, resumable=True)
  #   self.assertEqual('image/png', upload.mimetype())
  #   self.assertEqual(190, upload.size())
  #   self.assertEqual(True, upload.resumable())
  #   self.assertEqual(500, upload.chunksize())
  #   self.assertEqual('PNG', upload.getbytes(1, 3))
  #   f.close()

  def test_media_io_base_upload_from_bytes(self):
    try:
      f = open(datafile('small.png'), 'rb')
      fd = BytesIO(f.read())
      f.close()
      upload = MediaIoBaseUpload(
          fd=fd, mimetype='image/png', chunksize=500, resumable=True)
      self.assertEqual('image/png', upload.mimetype())
      self.assertEqual(190, upload.size())
      self.assertEqual(True, upload.resumable())
      self.assertEqual(500, upload.chunksize())
      self.assertEqual(b'PNG', upload.getbytes(1, 3))
    except ImportError:
      pass

  def test_media_io_base_upload_raises_on_invalid_chunksize(self):
    try:
      f = open(datafile('small.png'), 'rb')
      fd = BytesIO(f.read())
      f.close()
      self.assertRaises(InvalidChunkSizeError, MediaIoBaseUpload,
                        fd, 'image/png', chunksize=-2, resumable=True)
    except ImportError:
      pass

  def test_media_io_base_upload_streamable(self):
    try:
      fd = BytesIO(b'stuff')
      upload = MediaIoBaseUpload(
          fd=fd, mimetype='image/png', chunksize=500, resumable=True)
      self.assertEqual(True, upload.has_stream())
      self.assertEqual(fd, upload.stream())
    except ImportError:
      pass

  def test_media_io_base_next_chunk_retries(self):
    f = open(datafile('small.png'), 'rb')
    fd = BytesIO(f.read())
    upload = MediaIoBaseUpload(
        fd=fd, mimetype='image/png', chunksize=500, resumable=True)

    # Simulate 5XXs for both the request that creates the resumable upload and
    # the upload itself.
    http = HttpMockSequence([
      ({'status': '500'}, ''),
      ({'status': '500'}, ''),
      ({'status': '503'}, ''),
      ({'status': '200', 'location': 'location'}, ''),
      ({'status': '500'}, ''),
      ({'status': '500'}, ''),
      ({'status': '503'}, ''),
      ({'status': '200'}, '{}'),
    ])

    model = JsonModel()
    uri = u'https://www.googleapis.com/someapi/v1/upload/?foo=bar'
    method = u'POST'
    request = HttpRequest(
        http,
        model.response,
        uri,
        method=method,
        headers={},
        resumable=upload)

    sleeptimes = []
    request._sleep = lambda x: sleeptimes.append(x)
    request._rand = lambda: 10

    request.execute(num_retries=3)
    self.assertEqual([20, 40, 80, 20, 40, 80], sleeptimes)


class TestMediaIoBaseDownload(unittest.TestCase):

  def setUp(self):
    http = HttpMock(datafile('zoo.json'), {'status': '200'})
    zoo = build('zoo', 'v1', http=http)
    self.request = zoo.animals().get_media(name='Lion')
    self.fd = BytesIO()

  def test_media_io_base_download(self):
    self.request.http = HttpMockSequence([
      ({'status': '200',
        'content-range': '0-2/5'}, b'123'),
      ({'status': '200',
        'content-range': '3-4/5'}, b'45'),
    ])
    self.assertEqual(True, self.request.http.follow_redirects)

    download = MediaIoBaseDownload(
        fd=self.fd, request=self.request, chunksize=3)

    self.assertEqual(self.fd, download._fd)
    self.assertEqual(3, download._chunksize)
    self.assertEqual(0, download._progress)
    self.assertEqual(None, download._total_size)
    self.assertEqual(False, download._done)
    self.assertEqual(self.request.uri, download._uri)

    status, done = download.next_chunk()

    self.assertEqual(self.fd.getvalue(), b'123')
    self.assertEqual(False, done)
    self.assertEqual(3, download._progress)
    self.assertEqual(5, download._total_size)
    self.assertEqual(3, status.resumable_progress)

    status, done = download.next_chunk()

    self.assertEqual(self.fd.getvalue(), b'12345')
    self.assertEqual(True, done)
    self.assertEqual(5, download._progress)
    self.assertEqual(5, download._total_size)

  def test_media_io_base_download_handle_redirects(self):
    self.request.http = HttpMockSequence([
      ({'status': '200',
        'content-location': 'https://secure.example.net/lion'}, b''),
      ({'status': '200',
        'content-range': '0-2/5'}, b'abc'),
    ])

    download = MediaIoBaseDownload(
        fd=self.fd, request=self.request, chunksize=3)

    status, done = download.next_chunk()

    self.assertEqual('https://secure.example.net/lion', download._uri)

  def test_media_io_base_download_handle_4xx(self):
    self.request.http = HttpMockSequence([
      ({'status': '400'}, ''),
    ])

    download = MediaIoBaseDownload(
        fd=self.fd, request=self.request, chunksize=3)

    try:
      status, done = download.next_chunk()
      self.fail('Should raise an exception')
    except HttpError:
      pass

    # Even after raising an exception we can pick up where we left off.
    self.request.http = HttpMockSequence([
      ({'status': '200',
        'content-range': '0-2/5'}, b'123'),
    ])

    status, done = download.next_chunk()

    self.assertEqual(self.fd.getvalue(), b'123')

  def test_media_io_base_download_retries_5xx(self):
    self.request.http = HttpMockSequence([
      ({'status': '500'}, ''),
      ({'status': '500'}, ''),
      ({'status': '500'}, ''),
      ({'status': '200',
        'content-range': '0-2/5'}, b'123'),
      ({'status': '503'}, ''),
      ({'status': '503'}, ''),
      ({'status': '503'}, ''),
      ({'status': '200',
        'content-range': '3-4/5'}, b'45'),
    ])

    download = MediaIoBaseDownload(
        fd=self.fd, request=self.request, chunksize=3)

    self.assertEqual(self.fd, download._fd)
    self.assertEqual(3, download._chunksize)
    self.assertEqual(0, download._progress)
    self.assertEqual(None, download._total_size)
    self.assertEqual(False, download._done)
    self.assertEqual(self.request.uri, download._uri)

    # Set time.sleep and random.random stubs.
    sleeptimes = []
    download._sleep = lambda x: sleeptimes.append(x)
    download._rand = lambda: 10

    status, done = download.next_chunk(num_retries=3)

    # Check for exponential backoff using the rand function above.
    self.assertEqual([20, 40, 80], sleeptimes)

    self.assertEqual(self.fd.getvalue(), b'123')
    self.assertEqual(False, done)
    self.assertEqual(3, download._progress)
    self.assertEqual(5, download._total_size)
    self.assertEqual(3, status.resumable_progress)

    # Reset time.sleep stub.
    del sleeptimes[0:len(sleeptimes)]

    status, done = download.next_chunk(num_retries=3)

    # Check for exponential backoff using the rand function above.
    self.assertEqual([20, 40, 80], sleeptimes)

    self.assertEqual(self.fd.getvalue(), b'12345')
    self.assertEqual(True, done)
    self.assertEqual(5, download._progress)
    self.assertEqual(5, download._total_size)

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
Content-Type: application/json
Content-Length: 14
ETag: "etag/pony"\r\n\r\n{"answer": 42}"""


BATCH_RESPONSE = """--batch_foobarbaz
Content-Type: application/http
Content-Transfer-Encoding: binary
Content-ID: <randomness+1>

HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 14
ETag: "etag/pony"\r\n\r\n{"foo": 42}

--batch_foobarbaz
Content-Type: application/http
Content-Transfer-Encoding: binary
Content-ID: <randomness+2>

HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 14
ETag: "etag/sheep"\r\n\r\n{"baz": "qux"}
--batch_foobarbaz--"""


BATCH_ERROR_RESPONSE = """--batch_foobarbaz
Content-Type: application/http
Content-Transfer-Encoding: binary
Content-ID: <randomness+1>

HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 14
ETag: "etag/pony"\r\n\r\n{"foo": 42}

--batch_foobarbaz
Content-Type: application/http
Content-Transfer-Encoding: binary
Content-ID: <randomness+2>

HTTP/1.1 403 Access Not Configured
Content-Type: application/json
Content-Length: 245
ETag: "etag/sheep"\r\n\r\n{
 "error": {
  "errors": [
   {
    "domain": "usageLimits",
    "reason": "accessNotConfigured",
    "message": "Access Not Configured",
    "debugInfo": "QuotaState: BLOCKED"
   }
  ],
  "code": 403,
  "message": "Access Not Configured"
 }
}

--batch_foobarbaz--"""


BATCH_RESPONSE_WITH_401 = """--batch_foobarbaz
Content-Type: application/http
Content-Transfer-Encoding: binary
Content-ID: <randomness+1>

HTTP/1.1 401 Authorization Required
Content-Type: application/json
Content-Length: 14
ETag: "etag/pony"\r\n\r\n{"error": {"message":
  "Authorizaton failed."}}

--batch_foobarbaz
Content-Type: application/http
Content-Transfer-Encoding: binary
Content-ID: <randomness+2>

HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 14
ETag: "etag/sheep"\r\n\r\n{"baz": "qux"}
--batch_foobarbaz--"""


BATCH_SINGLE_RESPONSE = """--batch_foobarbaz
Content-Type: application/http
Content-Transfer-Encoding: binary
Content-ID: <randomness+1>

HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 14
ETag: "etag/pony"\r\n\r\n{"foo": 42}
--batch_foobarbaz--"""


class Callbacks(object):
  def __init__(self):
    self.responses = {}
    self.exceptions = {}

  def f(self, request_id, response, exception):
    self.responses[request_id] = response
    self.exceptions[request_id] = exception


class TestHttpRequest(unittest.TestCase):
  def test_unicode(self):
    http = HttpMock(datafile('zoo.json'), headers={'status': '200'})
    model = JsonModel()
    uri = u'https://www.googleapis.com/someapi/v1/collection/?foo=bar'
    method = u'POST'
    request = HttpRequest(
        http,
        model.response,
        uri,
        method=method,
        body=u'{}',
        headers={'content-type': 'application/json'})
    request.execute()
    self.assertEqual(uri, http.uri)
    self.assertEqual(str, type(http.uri))
    self.assertEqual(method, http.method)
    self.assertEqual(str, type(http.method))

  def test_retry(self):
    num_retries = 5
    resp_seq = [({'status': '500'}, '')] * num_retries
    resp_seq.append(({'status': '200'}, '{}'))

    http = HttpMockSequence(resp_seq)
    model = JsonModel()
    uri = u'https://www.googleapis.com/someapi/v1/collection/?foo=bar'
    method = u'POST'
    request = HttpRequest(
        http,
        model.response,
        uri,
        method=method,
        body=u'{}',
        headers={'content-type': 'application/json'})

    sleeptimes = []
    request._sleep = lambda x: sleeptimes.append(x)
    request._rand = lambda: 10

    request.execute(num_retries=num_retries)

    self.assertEqual(num_retries, len(sleeptimes))
    for retry_num in range(num_retries):
      self.assertEqual(10 * 2 ** (retry_num + 1), sleeptimes[retry_num])

  def test_no_retry_fails_fast(self):
    http = HttpMockSequence([
        ({'status': '500'}, ''),
        ({'status': '200'}, '{}')
    ])
    model = JsonModel()
    uri = u'https://www.googleapis.com/someapi/v1/collection/?foo=bar'
    method = u'POST'
    request = HttpRequest(
        http,
        model.response,
        uri,
        method=method,
        body=u'{}',
        headers={'content-type': 'application/json'})

    request._rand = lambda: 1.0
    request._sleep = lambda _: self.fail('sleep should not have been called.')

    try:
      request.execute()
      self.fail('Should have raised an exception.')
    except HttpError:
      pass


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
        body=u'{}',
        headers={'content-type': 'application/json'},
        methodId=None,
        resumable=None)
    s = batch._serialize_request(request).splitlines()
    self.assertEqual(EXPECTED.splitlines(), s)

  def test_serialize_request_media_body(self):
    batch = BatchHttpRequest()
    f = open(datafile('small.png'), 'rb')
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
    # Just testing it shouldn't raise an exception.
    s = batch._serialize_request(request).splitlines()

  def test_serialize_request_no_body(self):
    batch = BatchHttpRequest()
    request = HttpRequest(
        None,
        None,
        'https://www.googleapis.com/someapi/v1/collection/?foo=bar',
        method='POST',
        body=b'',
        headers={'content-type': 'application/json'},
        methodId=None,
        resumable=None)
    s = batch._serialize_request(request).splitlines()
    self.assertEqual(NO_BODY_EXPECTED.splitlines(), s)

  def test_deserialize_response(self):
    batch = BatchHttpRequest()
    resp, content = batch._deserialize_response(RESPONSE)

    self.assertEqual(200, resp.status)
    self.assertEqual('OK', resp.reason)
    self.assertEqual(11, resp.version)
    self.assertEqual('{"answer": 42}', content)

  def test_new_id(self):
    batch = BatchHttpRequest()

    id_ = batch._new_id()
    self.assertEqual('1', id_)

    id_ = batch._new_id()
    self.assertEqual('2', id_)

    batch.add(self.request1, request_id='3')

    id_ = batch._new_id()
    self.assertEqual('4', id_)

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
    batch = BatchHttpRequest()
    callbacks = Callbacks()

    batch.add(self.request1, callback=callbacks.f)
    batch.add(self.request2, callback=callbacks.f)
    http = HttpMockSequence([
      ({'status': '200',
        'content-type': 'multipart/mixed; boundary="batch_foobarbaz"'},
       BATCH_RESPONSE),
    ])
    batch.execute(http=http)
    self.assertEqual({'foo': 42}, callbacks.responses['1'])
    self.assertEqual(None, callbacks.exceptions['1'])
    self.assertEqual({'baz': 'qux'}, callbacks.responses['2'])
    self.assertEqual(None, callbacks.exceptions['2'])

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
      batch.execute(http=http)
      self.fail('Should raise exception')
    except BatchError as e:
      boundary, _ = e.content.split(None, 1)
      self.assertEqual('--', boundary[:2])
      parts = e.content.split(boundary)
      self.assertEqual(4, len(parts))
      self.assertEqual('', parts[0])
      self.assertEqual('--', parts[3].rstrip())
      header = parts[1].splitlines()[1]
      self.assertEqual('Content-Type: application/http', header)

  def test_execute_refresh_and_retry_on_401(self):
    batch = BatchHttpRequest()
    callbacks = Callbacks()
    cred_1 = MockCredentials('Foo')
    cred_2 = MockCredentials('Bar')

    http = HttpMockSequence([
      ({'status': '200',
        'content-type': 'multipart/mixed; boundary="batch_foobarbaz"'},
       BATCH_RESPONSE_WITH_401),
      ({'status': '200',
        'content-type': 'multipart/mixed; boundary="batch_foobarbaz"'},
       BATCH_SINGLE_RESPONSE),
    ])

    creds_http_1 = HttpMockSequence([])
    cred_1.authorize(creds_http_1)

    creds_http_2 = HttpMockSequence([])
    cred_2.authorize(creds_http_2)

    self.request1.http = creds_http_1
    self.request2.http = creds_http_2

    batch.add(self.request1, callback=callbacks.f)
    batch.add(self.request2, callback=callbacks.f)
    batch.execute(http=http)

    self.assertEqual({'foo': 42}, callbacks.responses['1'])
    self.assertEqual(None, callbacks.exceptions['1'])
    self.assertEqual({'baz': 'qux'}, callbacks.responses['2'])
    self.assertEqual(None, callbacks.exceptions['2'])

    self.assertEqual(1, cred_1._refreshed)
    self.assertEqual(0, cred_2._refreshed)

    self.assertEqual(1, cred_1._authorized)
    self.assertEqual(1, cred_2._authorized)

    self.assertEqual(1, cred_2._applied)
    self.assertEqual(2, cred_1._applied)

  def test_http_errors_passed_to_callback(self):
    batch = BatchHttpRequest()
    callbacks = Callbacks()
    cred_1 = MockCredentials('Foo')
    cred_2 = MockCredentials('Bar')

    http = HttpMockSequence([
      ({'status': '200',
        'content-type': 'multipart/mixed; boundary="batch_foobarbaz"'},
       BATCH_RESPONSE_WITH_401),
      ({'status': '200',
        'content-type': 'multipart/mixed; boundary="batch_foobarbaz"'},
       BATCH_RESPONSE_WITH_401),
    ])

    creds_http_1 = HttpMockSequence([])
    cred_1.authorize(creds_http_1)

    creds_http_2 = HttpMockSequence([])
    cred_2.authorize(creds_http_2)

    self.request1.http = creds_http_1
    self.request2.http = creds_http_2

    batch.add(self.request1, callback=callbacks.f)
    batch.add(self.request2, callback=callbacks.f)
    batch.execute(http=http)

    self.assertEqual(None, callbacks.responses['1'])
    self.assertEqual(401, callbacks.exceptions['1'].resp.status)
    self.assertEqual(
        'Authorization Required', callbacks.exceptions['1'].resp.reason)
    self.assertEqual({u'baz': u'qux'}, callbacks.responses['2'])
    self.assertEqual(None, callbacks.exceptions['2'])

  def test_execute_global_callback(self):
    callbacks = Callbacks()
    batch = BatchHttpRequest(callback=callbacks.f)

    batch.add(self.request1)
    batch.add(self.request2)
    http = HttpMockSequence([
      ({'status': '200',
        'content-type': 'multipart/mixed; boundary="batch_foobarbaz"'},
       BATCH_RESPONSE),
    ])
    batch.execute(http=http)
    self.assertEqual({'foo': 42}, callbacks.responses['1'])
    self.assertEqual({'baz': 'qux'}, callbacks.responses['2'])

  def test_execute_batch_http_error(self):
    callbacks = Callbacks()
    batch = BatchHttpRequest(callback=callbacks.f)

    batch.add(self.request1)
    batch.add(self.request2)
    http = HttpMockSequence([
      ({'status': '200',
        'content-type': 'multipart/mixed; boundary="batch_foobarbaz"'},
       BATCH_ERROR_RESPONSE),
    ])
    batch.execute(http=http)
    self.assertEqual({'foo': 42}, callbacks.responses['1'])
    expected = ('<HttpError 403 when requesting '
                'https://www.googleapis.com/someapi/v1/collection/?foo=bar returned '
                '"Access Not Configured">')
    self.assertEqual(expected, str(callbacks.exceptions['2']))


class TestRequestUriTooLong(unittest.TestCase):

  def test_turn_get_into_post(self):

    def _postproc(resp, content):
      return content

    http = HttpMockSequence([
      ({'status': '200'},
       'echo_request_body'),
      ({'status': '200'},
       'echo_request_headers'),
    ])

    # Send a long query parameter.
    query = {'q': 'a' * MAX_URI_LENGTH + '?&'}
    req = HttpRequest(
        http,
        _postproc,
        'http://example.com?' + urlencode(query),
        method='GET',
        body=None,
        headers={},
        methodId='foo',
        resumable=None)

    # Query parameters should be sent in the body.
    response = req.execute()
    self.assertEqual('q=' + 'a' * MAX_URI_LENGTH + '%3F%26', response)

    # Extra headers should be set.
    response = req.execute()
    self.assertEqual('GET', response['x-http-method-override'])
    self.assertEqual(str(MAX_URI_LENGTH + 8), response['content-length'])
    self.assertEqual(
        'application/x-www-form-urlencoded', response['content-type'])


class TestStreamSlice(unittest.TestCase):
  """Test _StreamSlice."""

  def setUp(self):
    self.stream = BytesIO(b'0123456789')

  def test_read(self):
    s = _StreamSlice(self.stream, 0, 4)
    self.assertEqual(b'', s.read(0))
    self.assertEqual(b'0', s.read(1))
    self.assertEqual(b'123', s.read())

  def test_read_too_much(self):
    s = _StreamSlice(self.stream, 1, 4)
    self.assertEqual(b'1234', s.read(6))

  def test_read_all(self):
    s = _StreamSlice(self.stream, 2, 1)
    self.assertEqual(b'2', s.read(-1))


class TestResponseCallback(unittest.TestCase):
  """Test adding callbacks to responses."""

  def test_ensure_response_callback(self):
    m = JsonModel()
    request = HttpRequest(
        None,
        m.response,
        'https://www.googleapis.com/someapi/v1/collection/?foo=bar',
        method='POST',
        body='{}',
        headers={'content-type': 'application/json'})
    h = HttpMockSequence([({'status': 200}, '{}')])
    responses = []

    def _on_response(resp, responses=responses):
      responses.append(resp)
    request.add_response_callback(_on_response)
    request.execute(http=h)
    self.assertEqual(1, len(responses))


if __name__ == '__main__':
  logging.getLogger().setLevel(logging.ERROR)
  unittest.main()
