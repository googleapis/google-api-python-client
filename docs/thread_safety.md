# Thread Safety

This page contains important information about the thread safety of this library.

## The httplib2.Http() objects are not thread-safe

The google-api-python-client library is built on top of the [httplib2](https://github.com/httplib2/httplib2) library, which is not thread-safe. Therefore, if you are running as a multi-threaded application, each thread that you are making requests from must have its own instance of `httplib2.Http()`.

The easiest way to provide threads with their own `httplib2.Http()` instances is to either override the construction of it within the service object or to pass an instance via the http argument to method calls.

```py
# Create a new Http() object for every request
def build_request(http, *args, **kwargs):
  new_http = httplib2.Http()
  return apiclient.http.HttpRequest(new_http, *args, **kwargs)
service = build('api_name', 'api_version', requestBuilder=build_request)

# Pass in a new Http() manually for every request
service = build('api_name', 'api_version')
http = httplib2.Http()
service.stamps().list().execute(http=http)
```

## Credential Storage objects are thread-safe

All [Storage](https://oauth2client.readthedocs.io/en/latest/source/oauth2client.client.html#oauth2client.client.Storage) objects defined in this library are thread-safe, and multiple processes and threads can operate on a single store.

In some cases, this library automatically refreshes expired OAuth 2.0 tokens. When many threads are sharing the same set of credentials, the threads cooperate to minimize the total number of token refresh requests sent to the server.
