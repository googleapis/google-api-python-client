# Copyright 2010 Google Inc. All Rights Reserved.

"""Classes to encapsulate a single HTTP request.

The classes implement a command pattern, with every
object supporting an execute() method that does the
actuall HTTP request.
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'
__all__ = [
    'HttpRequest', 'RequestMockBuilder'
    ]

import httplib2
from model import JsonModel


class HttpRequest(object):
  """Encapsulates a single HTTP request.
  """

  def __init__(self, http, uri, method="GET", body=None, headers=None,
               postproc=None, methodId=None):
    """Constructor for an HttpRequest.

    Only http and uri are required.

    Args:
      http: httplib2.Http, the transport object to use to make a request
      uri: string, the absolute URI to send the request to
      method: string, the HTTP method to use
      body: string, the request body of the HTTP request
      headers: dict, the HTTP request headers
      postproc: callable, called on the HTTP response and content to transform
                it into a data object before returning, or raising an exception
                on an error.
      methodId: string, a unique identifier for the API method being called.
    """
    self.uri = uri
    self.method = method
    self.body = body
    self.headers = headers or {}
    self.http = http
    self.postproc = postproc

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
    resp, content = http.request(self.uri, self.method,
                                      body=self.body,
                                      headers=self.headers)
    return self.postproc(resp, content)


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
    tuples of (httplib2.Response, content) that should be returned when that
    method is called. None may also be passed in for the httplib2.Response, in
    which case a 200 OK response will be generated.

    Example:
      response = '{"data": {"id": "tag:google.c...'
      requestBuilder = RequestMockBuilder(
        {
          'chili.activities.get': (None, response),
        }
      )
      apiclient.discovery.build("buzz", "v1", requestBuilder=requestBuilder)

    Methods that you do not supply a response for will return a
    200 OK with an empty string as the response content. The methodId
    is taken from the rpcName in the discovery document.

    For more details see the project wiki.
  """

  def __init__(self, responses):
    """Constructor for RequestMockBuilder

    The constructed object should be a callable object
    that can replace the class HttpResponse.

    responses - A dictionary that maps methodIds into tuples
                of (httplib2.Response, content). The methodId
                comes from the 'rpcName' field in the discovery
                document.
    """
    self.responses = responses

  def __call__(self, http, uri, method="GET", body=None, headers=None,
               postproc=None, methodId=None):
    """Implements the callable interface that discovery.build() expects
    of requestBuilder, which is to build an object compatible with
    HttpRequest.execute(). See that method for the description of the
    parameters and the expected response.
    """
    if methodId in self.responses:
      resp, content = self.responses[methodId]
      return HttpRequestMock(resp, content, postproc)
    else:
      model = JsonModel()
      return HttpRequestMock(None, '{}', model.response)
