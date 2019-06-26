# Performance Tips

This document covers techniques you can use to improve the performance of your application. The documentation for the specific API you are using should have a similar page with more detail on some of these topics. For example, see the [Performance Tips page for the Google Drive API](https://developers.google.com/drive/performance).

## About gzip

This client library requests gzip compression for all API responses and unzips the data for you. Although this requires additional CPU time to uncompress the results, the tradeoff with network costs usually makes it worthwhile.

## Partial response (fields parameter)

By default, the server sends back the full representation of a resource after processing requests. For better performance, you can ask the server to send only the fields you really need and get a _partial response_ instead.

To request a partial response, add the standard `fields` parameter to any API method. The value of this parameter specifies the fields you want returned. You can use this parameter with any request that returns response data.

In the following code snippet, the `list` method of a fictitious stamps API is called. The `cents` parameter is defined by the API to only return stamps with the given value. The value of the `fields` parameter is set to 'count,items/name'. The response will only contain stamps whose value is 5 cents, and the data returned will only include the number of stamps found along with the stamp names:

```py
response = service.stamps.list(cents=5, fields='count,items/name').execute()
```

Note how commas are used to delimit the desired fields, and slashes are used to indicate fields that are contained in parent fields. There are other formatting options for the `fields` parameter, and you should see the "Performance Tips" page in the documentation for the API you are using.

## Partial update (patch)

If the API you are calling supports patch, you can avoid sending unnecessary data when modifying resources. For these APIs, you can call the `patch()` method and supply the arguments you wish to modify for the resource. If supported, the API's PyDoc will have documentation for the `patch()` method.

For more information about patch semantics, see the "Performance Tips" page in the documentation for the API you are using.

## Cache

You should turn on caching at the `httplib2` level. The cache will store `ETags` associated with a resource and use them during future fetches and updates of the same resource.

To enable caching, pass in a cache implementation to the `httplib2.Http` constructor. In the simplest case, you can just pass in a directory name, and a cache will be built from that directory:

```py
http = httplib2.Http(cache=".cache")
```

On App Engine you can use memcache as a cache object:

```py
from google.appengine.api import memcache
http = httplib2.Http(cache=memcache)
```

## Batch

If you are sending many small requests you may benefit from [batching](batch.md), which allows those requests to be bundled into a single HTTP request.
