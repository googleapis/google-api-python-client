# Thread Safety

This page contains important information about the thread safety of this library.

## The httplib2.Http() objects are not thread-safe

The google-api-python-client library is built on top of the [httplib2](https://github.com/httplib2/httplib2) library, which is not thread-safe. Therefore, if you are running as a multi-threaded application, each thread that you are making requests from must have its own instance of `httplib2.Http()`.

The easiest way to provide threads with their own `httplib2.Http()` instances is to either override the construction of it within the service object or to pass an instance via the http argument to method calls.

```python
import google.auth
import googleapiclient
import google_auth_httplib2
import httplib2
from googleapiclient import discovery

# Create a new Http() object for every request
def build_request(http, *args, **kwargs):
  new_http = google_auth_httplib2.AuthorizedHttp(credentials, http=httplib2.Http())
  return googleapiclient.http.HttpRequest(new_http, *args, **kwargs)
service = discovery.build('api_name', 'api_version', requestBuilder=build_request)

# Pass in a new Http() manually for every request
service = discovery.build('api_name', 'api_version')
http = google_auth_httplib2.AuthorizedHttp(credentials, http=httplib2.Http())
service.stamps().list().execute(http=http)
```
