# Mocks

The use of [Mock objects](http://en.wikipedia.org/wiki/Mock_object) is a standard testing methodology for Python and other object-oriented languages. This library defines Mock classes that simulate responses to API calls. You can use them to test how your code handles basic interactions with Google APIs.

> **Note:** Many of the [Python Client Library test scripts](https://github.com/google/google-api-python-client/tree/master/tests) use these classes.

## HttpMock

This class simulates the response to a single HTTP request. As arguments, the constructor for the [HttpMock](https://google.github.io/google-api-python-client/docs/epy/googleapiclient.http.HttpMock-class.html) object takes a dictionary object representing the response header and the path to a file. When this resource built on this object is executed, it simply returns contents of the file.

### Example

This example uses `HttpMock` to simulate the basic steps necessary to complete an API call to the [Google Books API](https://developers.google.com/apis-explorer/#p/books/v1/). The first Mock HTTP returns a status code of 200 and a file named `books-discovery.json`, which is the discovery document that describes the Books API. This file is a necessary part of the building of the service object, which takes place in the next few lines. The actual request is executed using the second Mock object. This returns the contents of `books-android.json`, the simulated response.

```py
from apiclient.discovery import build
from apiclient.http import HttpMock
import pprint

http = HttpMock('books-discovery.json', {'status': '200'})
api_key = 'your_api_key'
service = build('books', 'v1', http=http, developerKey=api_key)
request = service.volumes().list(source='public', q='android')
http = HttpMock('books-android.json', {'status': '200'})
response = request.execute(http=http)
pprint.pprint(response)
```

> **Notes:**
> - To run this sample, it would not be necessary to replace the placeholder your_api_key with an actual key, since the Mock object does not actually call the API.
> - As you develop and test your application, it is a good idea to save actual API responses in files like books-discovery.json or books-android.json for use in testing.
> - Notice that a second HttpMock is created to simulate the second HTTP call.
> - The second use of the execute method demonstrates how you can re-use the request object by calling execute with another Mock object as an argument. (This would also work with an actual HTTP call.)

## HttpMockSequence

The [HttpMockSequence](https://google.github.io/google-api-python-client/docs/epy/googleapiclient.http.HttpMockSequence-class.html) class simulates the sequence of HTTP responses. Each response consists of a header (a dictionary) and a content object (which can be a reference to a file, a JSON-like data structure defined inline, or one of the keywords listed below). When the resource built from this Mock object is executed, it returns the series of responses, one by one.

### Special Values for simulated HTTP responses

Instead of a pre-defined object, your code can use one of the following keywords as the content object of a simulated HTTP response. At runtime, the Mock object returns the information described in the table.

<table>
  <tbody><tr>
    <th>
      Keyword
    </th>
    <th>
      Returns:
    </th>
  </tr>
  <tr>
    <td>
      <code><span>echo_request_headers</span></code>
    </td>
    <td>
      the complete request headers
    </td>
  </tr>
  <tr>
    <td>
      <code><span>echo_request_headers_as_json</span></code>
    </td>
    <td>
      the complete request headers as a json object
    </td>
  </tr>
  <tr>
    <td>
      <code><span>echo_request_body</span></code>
    </td>
    <td>
      the request body
    </td>
  </tr>
  <tr>
    <td>
      <code><span>echo_request_uri</span></code>
    </td>
    <td>
      the request uri
    </td>
  </tr></tbody>
</table>

### Example

The following code snippet combines the two HTTP call simulations from the previous snippet into a single Mock object. The object created using `HttpMockSequence` simulates the return of the discovery document from the `books.volume.list` service, then the return of the result of the 'android' query (built in to the `request` object). You could add code to this snipped to print the contents of `response`, test that it returned successfully, etc.

```py
from apiclient.discovery import build
from apiclient.http import HttpMockSequence

books_discovery = # Saved data from a build response
books_android = # Saved data from a request to list android volumes

http = HttpMockSequence([
    ({'status': '200'}, books_discovery),
    ({'status': '200'}, books_android)])
api_key = 'your_api_key'
service = build('books', 'v1',
                http=http,
                developerKey=your_api_key)
request = service.volumes().list(source='public', q='android')
response = request.execute()
```