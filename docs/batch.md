# Batch

<section>
  <p>
    Each HTTP connection that your application makes results in a certain amount of overhead.
    This library supports batching,
    to allow your application to put several API calls into a single HTTP request.
    Examples of situations when you might want to use batching:
  </p>
  <ul>
    <li>
      You have many small requests to make and would like to minimize HTTP request overhead.
    </li>
    <li>
      A user made changes to data while your application was offline,
      so your application needs to synchronize its local data with the server
      by sending a lot of updates and deletes.
    </li>
  </ul>
  <p class="note">
    <strong>Note</strong>: You're limited to 1000 calls in a single batch request.
    If you need to make more calls than that, use multiple batch requests.
  </p>
  <p class="note">
    <strong>Note</strong>: You cannot use a
    <a href="/api-client-library/python/guide/media_upload">media upload</a>
    object in a batch request.
  </p>
</section>

<section>
  <h2>Details</h2>
  <p>
    You create batch requests by calling <code>new_batch_http_request()</code> on your service
    object, which returns a
    <a href="https://google.github.io/google-api-python-client/docs/epy/googleapiclient.http.BatchHttpRequest-class.html">BatchHttpRequest</a>
    object, and then calling <code>add()</code> for each request you want to execute.
    You may pass in a callback with each request that is called with the response to that request.
    The callback function arguments are:
    a unique request identifier for each API call,
    a response object which contains the API call response,
    and an exception object which may be set to an exception raised by the API call.
    After you've added the requests, you call <code>execute()</code> to make the requests.
    The <code>execute()</code> function blocks until all callbacks have been called.
  </p>
  <p>
    In the following code snippet,
    two API requests are batched to a single HTTP request,
    and each API request is supplied a callback:
  </p>
  <pre class="prettyprint">
See below</pre>
  <p>
    You can also supply a single callback that gets called for each response:
  </p>
  <pre class="prettyprint">See below</pre>
  <p>
    The
    <a href="https://google.github.io/google-api-python-client/docs/epy/googleapiclient.http.BatchHttpRequest-class.html#add">add()</a>
    method also allows you to supply a <code>request_id</code> parameter for each request.
    These IDs are provided to the callbacks.
    If you don't supply one, the library creates one for you.
    The IDs must be unique for each API request,
    otherwise <code>add()</code> raises an exception.
  </p>
  <p>
    If you supply a callback to both <code>new_batch_http_request()</code> and <code>add()</code>, they both get called.
  </p>
</section>

---

```py
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
batch.execute(http=http)
```

```py

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
batch.execute(http=http)
