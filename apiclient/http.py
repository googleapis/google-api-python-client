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

"""Classes to encapsulate a single HTTP request.

The classes implement a command pattern, with every
object supporting an execute() method that does the
actuall HTTP request.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'
__all__ = [
    'HttpRequest', 'RequestMockBuilder', 'HttpMock'
    'set_user_agent', 'tunnel_patch'
    ]

import copy
import httplib2
import os
import mimeparse
import mimetypes

from model import JsonModel
from errors import HttpError
from errors import ResumableUploadError
from errors import UnexpectedBodyError
from errors import UnexpectedMethodError
from anyjson import simplejson


class MediaUploadProgress(object):
  """Status of a resumable upload."""

  def __init__(self, resumable_progress, total_size):
    """Constructor.

    Args:
      resumable_progress: int, bytes sent so far.
      total_size: int, total bytes in complete upload.
    """
    self.resumable_progress = resumable_progress
    self.total_size = total_size

  def progress(self):
    """Percent of upload completed, as a float."""
    return float(self.resumable_progress)/float(self.total_size)


class MediaUpload(object):
  """Describes a media object to upload.

  Base class that defines the interface of MediaUpload subclasses.
  """

  def getbytes(self, begin, end):
    raise NotImplementedError()

  def size(self):
    raise NotImplementedError()

  def chunksize(self):
    raise NotImplementedError()

  def mimetype(self):
    return 'application/octet-stream'

  def resumable(self):
    return False

  def _to_json(self, strip=None):
    """Utility function for creating a JSON representation of a MediaUpload.

    Args:
      strip: array, An array of names of members to not include in the JSON.

    Returns:
       string, a JSON representation of this instance, suitable to pass to
       from_json().
    """
    t = type(self)
    d = copy.copy(self.__dict__)
    if strip is not None:
      for member in strip:
        del d[member]
    d['_class'] = t.__name__
    d['_module'] = t.__module__
    return simplejson.dumps(d)

  def to_json(self):
    """Create a JSON representation of an instance of MediaUpload.

    Returns:
       string, a JSON representation of this instance, suitable to pass to
       from_json().
    """
    return self._to_json()

  @classmethod
  def new_from_json(cls, s):
    """Utility class method to instantiate a MediaUpload subclass from a JSON
    representation produced by to_json().

    Args:
      s: string, JSON from to_json().

    Returns:
      An instance of the subclass of MediaUpload that was serialized with
      to_json().
    """
    data = simplejson.loads(s)
    # Find and call the right classmethod from_json() to restore the object.
    module = data['_module']
    m = __import__(module, fromlist=module.split('.')[:-1])
    kls = getattr(m, data['_class'])
    from_json = getattr(kls, 'from_json')
    return from_json(s)

class MediaFileUpload(MediaUpload):
  """A MediaUpload for a file.

  Construct a MediaFileUpload and pass as the media_body parameter of the
  method. For example, if we had a service that allowed uploading images:


    media = MediaFileUpload('smiley.png', mimetype='image/png', chunksize=1000,
                    resumable=True)
    service.objects().insert(
        bucket=buckets['items'][0]['id'],
        name='smiley.png',
        media_body=media).execute()
  """

  def __init__(self, filename, mimetype=None, chunksize=10000, resumable=False):
    """Constructor.

    Args:
      filename: string, Name of the file.
      mimetype: string, Mime-type of the file. If None then a mime-type will be
        guessed from the file extension.
      chunksize: int, File will be uploaded in chunks of this many bytes. Only
        used if resumable=True.
      resumable: bool, True if this is a resumable upload. False means upload in
        a single request.
    """
    self._filename = filename
    self._size = os.path.getsize(filename)
    self._fd = None
    if mimetype is None:
      (mimetype, encoding) = mimetypes.guess_type(filename)
    self._mimetype = mimetype
    self._chunksize = chunksize
    self._resumable = resumable

  def mimetype(self):
    return self._mimetype

  def size(self):
    return self._size

  def chunksize(self):
    return self._chunksize

  def resumable(self):
    return self._resumable

  def getbytes(self, begin, length):
    """Get bytes from the media.

    Args:
      begin: int, offset from beginning of file.
      length: int, number of bytes to read, starting at begin.

    Returns:
      A string of bytes read. May be shorted than length if EOF was reached
      first.
    """
    if self._fd is None:
      self._fd = open(self._filename, 'rb')
    self._fd.seek(begin)
    return self._fd.read(length)

  def to_json(self):
    """Creating a JSON representation of an instance of Credentials.

    Returns:
       string, a JSON representation of this instance, suitable to pass to
       from_json().
    """
    return self._to_json(['_fd'])

  @staticmethod
  def from_json(s):
    d = simplejson.loads(s)
    return MediaFileUpload(
        d['_filename'], d['_mimetype'], d['_chunksize'], d['_resumable'])


class HttpRequest(object):
  """Encapsulates a single HTTP request.
  """

  def __init__(self, http, postproc, uri,
               method='GET',
               body=None,
               headers=None,
               methodId=None,
               resumable=None):
    """Constructor for an HttpRequest.

    Args:
      http: httplib2.Http, the transport object to use to make a request
      postproc: callable, called on the HTTP response and content to transform
                it into a data object before returning, or raising an exception
                on an error.
      uri: string, the absolute URI to send the request to
      method: string, the HTTP method to use
      body: string, the request body of the HTTP request,
      headers: dict, the HTTP request headers
      methodId: string, a unique identifier for the API method being called.
      resumable: MediaUpload, None if this is not a resumbale request.
    """
    self.uri = uri
    self.method = method
    self.body = body
    self.headers = headers or {}
    self.methodId = methodId
    self.http = http
    self.postproc = postproc
    self.resumable = resumable

    major, minor, params = mimeparse.parse_mime_type(
        headers.get('content-type', 'application/json'))
    self.multipart_boundary = params.get('boundary', '').strip('"')

    # If this was a multipart resumable, the size of the non-media part.
    self.multipart_size = 0

    # The resumable URI to send chunks to.
    self.resumable_uri = None

    # The bytes that have been uploaded.
    self.resumable_progress = 0

    if resumable is not None:
      if self.body is not None:
        self.multipart_size = len(self.body)
      else:
        self.multipart_size = 0
      self.total_size = self.resumable.size() + self.multipart_size + len(self.multipart_boundary)

  def execute(self, http=None):
    """Execute the request.

    Args:
      http: httplib2.Http, an http object to be used in place of the
            one the HttpRequest request object was constructed with.

    Returns:
      A deserialized object model of the response body as determined
      by the postproc.

    Raises:
      apiclient.errors.HttpError if the response was not a 2xx.
      httplib2.Error if a transport error has occured.
    """
    if http is None:
      http = self.http
    if self.resumable:
      body = None
      while body is None:
        _, body = self.next_chunk(http)
      return body
    else:
      resp, content = http.request(self.uri, self.method,
                                   body=self.body,
                                   headers=self.headers)

      if resp.status >= 300:
        raise HttpError(resp, content, self.uri)
    return self.postproc(resp, content)

  def next_chunk(self, http=None):
    """Execute the next step of a resumable upload.

    Can only be used if the method being executed supports media uploads and the
    MediaUpload object passed in was flagged as using resumable upload.

    Example:

      media = MediaFileUpload('smiley.png', mimetype='image/png', chunksize=1000,
                              resumable=True)
      request = service.objects().insert(
          bucket=buckets['items'][0]['id'],
          name='smiley.png',
          media_body=media)

      response = None
      while response is None:
        status, response = request.next_chunk()
        if status:
          print "Upload %d%% complete." % int(status.progress() * 100)


    Returns:
      (status, body): (ResumableMediaStatus, object)
         The body will be None until the resumable media is fully uploaded.
    """
    if http is None:
      http = self.http

    if self.resumable_uri is None:
      start_headers = copy.copy(self.headers)
      start_headers['X-Upload-Content-Type'] = self.resumable.mimetype()
      start_headers['X-Upload-Content-Length'] = str(self.resumable.size())
      start_headers['Content-Length'] = '0'
      resp, content = http.request(self.uri, self.method,
                                   body="",
                                   headers=start_headers)
      if resp.status == 200 and 'location' in resp:
        self.resumable_uri = resp['location']
      else:
        raise ResumableUploadError("Failed to retrieve starting URI.")
    if self.body:
      begin = 0
      data = self.body
    else:
      begin = self.resumable_progress - self.multipart_size
      data = self.resumable.getbytes(begin, self.resumable.chunksize())

    # Tack on the multipart/related boundary if we are at the end of the file.
    if begin + self.resumable.chunksize() >= self.resumable.size():
      data += self.multipart_boundary
    headers = {
        'Content-Range': 'bytes %d-%d/%d' % (
            self.resumable_progress, self.resumable_progress + len(data) - 1,
            self.total_size),
        }
    resp, content = http.request(self.resumable_uri, 'PUT',
                                 body=data,
                                 headers=headers)
    if resp.status in [200, 201]:
      return None, self.postproc(resp, content)
    # A "308 Resume Incomplete" indicates we are not done.
    elif resp.status == 308:
      self.resumable_progress = int(resp['range'].split('-')[1]) + 1
      if self.resumable_progress >= self.multipart_size:
        self.body = None
      if 'location' in resp:
        self.resumable_uri = resp['location']
    else:
      raise HttpError(resp, content, self.uri)

    return MediaUploadProgress(self.resumable_progress, self.total_size), None

  def to_json(self):
    """Returns a JSON representation of the HttpRequest."""
    d = copy.copy(self.__dict__)
    if d['resumable'] is not None:
      d['resumable'] = self.resumable.to_json()
    del d['http']
    del d['postproc']
    return simplejson.dumps(d)

  @staticmethod
  def from_json(s, http, postproc):
    """Returns an HttpRequest populated with info from a JSON object."""
    d = simplejson.loads(s)
    if d['resumable'] is not None:
      d['resumable'] = MediaUpload.new_from_json(d['resumable'])
    return HttpRequest(
        http,
        postproc,
        uri = d['uri'],
        method= d['method'],
        body=d['body'],
        headers=d['headers'],
        methodId=d['methodId'],
        resumable=d['resumable'])


class HttpRequestMock(object):
  """Mock of HttpRequest.

  Do not construct directly, instead use RequestMockBuilder.
  """

  def __init__(self, resp, content, postproc):
    """Constructor for HttpRequestMock

    Args:
      resp: httplib2.Response, the response to emulate coming from the request
      content: string, the response body
      postproc: callable, the post processing function usually supplied by
                the model class. See model.JsonModel.response() as an example.
    """
    self.resp = resp
    self.content = content
    self.postproc = postproc
    if resp is None:
      self.resp = httplib2.Response({'status': 200, 'reason': 'OK'})
    if 'reason' in self.resp:
      self.resp.reason = self.resp['reason']

  def execute(self, http=None):
    """Execute the request.

    Same behavior as HttpRequest.execute(), but the response is
    mocked and not really from an HTTP request/response.
    """
    return self.postproc(self.resp, self.content)


class RequestMockBuilder(object):
  """A simple mock of HttpRequest

    Pass in a dictionary to the constructor that maps request methodIds to
    tuples of (httplib2.Response, content, opt_expected_body) that should be
    returned when that method is called. None may also be passed in for the
    httplib2.Response, in which case a 200 OK response will be generated.
    If an opt_expected_body (str or dict) is provided, it will be compared to
    the body and UnexpectedBodyError will be raised on inequality.

    Example:
      response = '{"data": {"id": "tag:google.c...'
      requestBuilder = RequestMockBuilder(
        {
          'plus.activities.get': (None, response),
        }
      )
      apiclient.discovery.build("plus", "v1", requestBuilder=requestBuilder)

    Methods that you do not supply a response for will return a
    200 OK with an empty string as the response content or raise an excpetion if
    check_unexpected is set to True. The methodId is taken from the rpcName
    in the discovery document.

    For more details see the project wiki.
  """

  def __init__(self, responses, check_unexpected=False):
    """Constructor for RequestMockBuilder

    The constructed object should be a callable object
    that can replace the class HttpResponse.

    responses - A dictionary that maps methodIds into tuples
                of (httplib2.Response, content). The methodId
                comes from the 'rpcName' field in the discovery
                document.
    check_unexpected - A boolean setting whether or not UnexpectedMethodError
                       should be raised on unsupplied method.
    """
    self.responses = responses
    self.check_unexpected = check_unexpected

  def __call__(self, http, postproc, uri, method='GET', body=None,
               headers=None, methodId=None, resumable=None):
    """Implements the callable interface that discovery.build() expects
    of requestBuilder, which is to build an object compatible with
    HttpRequest.execute(). See that method for the description of the
    parameters and the expected response.
    """
    if methodId in self.responses:
      response = self.responses[methodId]
      resp, content = response[:2]
      if len(response) > 2:
        # Test the body against the supplied expected_body.
        expected_body = response[2]
        if bool(expected_body) != bool(body):
          # Not expecting a body and provided one
          # or expecting a body and not provided one.
          raise UnexpectedBodyError(expected_body, body)
        if isinstance(expected_body, str):
          expected_body = simplejson.loads(expected_body)
        body = simplejson.loads(body)
        if body != expected_body:
          raise UnexpectedBodyError(expected_body, body)
      return HttpRequestMock(resp, content, postproc)
    elif self.check_unexpected:
      raise UnexpectedMethodError(methodId)
    else:
      model = JsonModel(False)
      return HttpRequestMock(None, '{}', model.response)


class HttpMock(object):
  """Mock of httplib2.Http"""

  def __init__(self, filename, headers=None):
    """
    Args:
      filename: string, absolute filename to read response from
      headers: dict, header to return with response
    """
    if headers is None:
      headers = {'status': '200 OK'}
    f = file(filename, 'r')
    self.data = f.read()
    f.close()
    self.headers = headers

  def request(self, uri,
              method='GET',
              body=None,
              headers=None,
              redirections=1,
              connection_type=None):
    return httplib2.Response(self.headers), self.data


class HttpMockSequence(object):
  """Mock of httplib2.Http

  Mocks a sequence of calls to request returning different responses for each
  call. Create an instance initialized with the desired response headers
  and content and then use as if an httplib2.Http instance.

    http = HttpMockSequence([
      ({'status': '401'}, ''),
      ({'status': '200'}, '{"access_token":"1/3w","expires_in":3600}'),
      ({'status': '200'}, 'echo_request_headers'),
      ])
    resp, content = http.request("http://examples.com")

  There are special values you can pass in for content to trigger
  behavours that are helpful in testing.

  'echo_request_headers' means return the request headers in the response body
  'echo_request_headers_as_json' means return the request headers in
     the response body
  'echo_request_body' means return the request body in the response body
  'echo_request_uri' means return the request uri in the response body
  """

  def __init__(self, iterable):
    """
    Args:
      iterable: iterable, a sequence of pairs of (headers, body)
    """
    self._iterable = iterable

  def request(self, uri,
              method='GET',
              body=None,
              headers=None,
              redirections=1,
              connection_type=None):
    resp, content = self._iterable.pop(0)
    if content == 'echo_request_headers':
      content = headers
    elif content == 'echo_request_headers_as_json':
      content = simplejson.dumps(headers)
    elif content == 'echo_request_body':
      content = body
    elif content == 'echo_request_uri':
      content = uri
    return httplib2.Response(resp), content


def set_user_agent(http, user_agent):
  """Set the user-agent on every request.

  Args:
     http - An instance of httplib2.Http
         or something that acts like it.
     user_agent: string, the value for the user-agent header.

  Returns:
     A modified instance of http that was passed in.

  Example:

    h = httplib2.Http()
    h = set_user_agent(h, "my-app-name/6.0")

  Most of the time the user-agent will be set doing auth, this is for the rare
  cases where you are accessing an unauthenticated endpoint.
  """
  request_orig = http.request

  # The closure that will replace 'httplib2.Http.request'.
  def new_request(uri, method='GET', body=None, headers=None,
                  redirections=httplib2.DEFAULT_MAX_REDIRECTS,
                  connection_type=None):
    """Modify the request headers to add the user-agent."""
    if headers is None:
      headers = {}
    if 'user-agent' in headers:
      headers['user-agent'] = user_agent + ' ' + headers['user-agent']
    else:
      headers['user-agent'] = user_agent
    resp, content = request_orig(uri, method, body, headers,
                        redirections, connection_type)
    return resp, content

  http.request = new_request
  return http


def tunnel_patch(http):
  """Tunnel PATCH requests over POST.
  Args:
     http - An instance of httplib2.Http
         or something that acts like it.

  Returns:
     A modified instance of http that was passed in.

  Example:

    h = httplib2.Http()
    h = tunnel_patch(h, "my-app-name/6.0")

  Useful if you are running on a platform that doesn't support PATCH.
  Apply this last if you are using OAuth 1.0, as changing the method
  will result in a different signature.
  """
  request_orig = http.request

  # The closure that will replace 'httplib2.Http.request'.
  def new_request(uri, method='GET', body=None, headers=None,
                  redirections=httplib2.DEFAULT_MAX_REDIRECTS,
                  connection_type=None):
    """Modify the request headers to add the user-agent."""
    if headers is None:
      headers = {}
    if method == 'PATCH':
      if 'oauth_token' in headers.get('authorization', ''):
        logging.warning(
            'OAuth 1.0 request made with Credentials after tunnel_patch.')
      headers['x-http-method-override'] = "PATCH"
      method = 'POST'
    resp, content = request_orig(uri, method, body, headers,
                        redirections, connection_type)
    return resp, content

  http.request = new_request
  return http
