# Batch

Each HTTP connection that your application makes results in a certain amount of overhead.
This library supports batching,
to allow your application to put several API calls into a single HTTP request.
Examples of situations when you might want to use batching:
* You have many small requests to make and would like to minimize HTTP request overhead.
* A user made changes to data while your application was offline,
  so your application needs to synchronize its local data with the server
  by sending a lot of updates and deletes.
  
**Note**: You're limited to 1000 calls in a single batch request.
If you need to make more calls than that, use multiple batch requests.

**Note**: You cannot use a
[media upload](/api-client-library/python/guide/media_upload)
object in a batch request.

## Details
You create batch requests by calling `new_batch_http_request()` on your service
object, which returns a
[BatchHttpRequest](https://google.github.io/google-api-python-client/docs/epy/googleapiclient.http.BatchHttpRequest-class.html)
object, and then calling `add()` for each request you want to execute.
You may pass in a callback with each request that is called with the response to that request.
The callback function arguments are:
a unique request identifier for each API call,
a response object which contains the API call response,
and an exception object which may be set to an exception raised by the API call.
After you've added the requests, you call `execute()` to make the requests.
The `execute()` function blocks until all callbacks have been called.

In the following code snippet,
two API requests are batched to a single HTTP request,
and each API request is supplied a callback:
  <pre class="prettyprint">
See below</pre>
You can also supply a single callback that gets called for each response:

  <pre class="prettyprint">See below</pre>

The
[add()](https://google.github.io/google-api-python-client/docs/epy/googleapiclient.http.BatchHttpRequest-class.html#add)
method also allows you to supply a <code>request_id</code> parameter for each request.
These IDs are provided to the callbacks.
If you don't supply one, the library creates one for you.
The IDs must be unique for each API request,
otherwise `add()` raises an exception.

If you supply a callback to both `new_batch_http_request()` and `add()`, they both get called.
 

---

```python
def list_animals(request_id, response, exception):
  if exception is not None:
    # Do something with the exception
    pass
  else:
    # Do something with the response
    pass

def list_farmers(request_id, response):
  """Do something with the farmers list response."""
  pass

service = build('farm', 'v2')

batch = service.new_batch_http_request()

batch.add(service.animals().list(), callback=list_animals)
batch.add(service.farmers().list(), callback=list_farmers)
batch.execute()
```

```python

def insert_animal(request_id, response, exception):
  if exception is not None:
    # Do something with the exception
    pass
  else:
    # Do something with the response
    pass

service = build('farm', 'v2')

batch = service.new_batch_http_request(callback=insert_animal)

batch.add(service.animals().insert(name="sheep"))
batch.add(service.animals().insert(name="pig"))
batch.add(service.animals().insert(name="llama"))
batch.execute()
```
