# Pagination

Some API methods may return very large lists of data. To reduce the response size, many of these API methods support pagination. With paginated results, your application can iteratively request and process large lists one page at a time. For API methods that support it, there exist similarly named methods with a `_next` suffix. For example, if a method is named `list()`, there may also be a method named `list_next()`. These methods can be found in the API's PyDoc documentation on the [Supported APIs page](dyn/index.md).

To process the first page of results, create a request object and call `execute()` as you normally would. For further pages, you call the corresponding `method_name_next()` method, and pass it the previous request and response. Continue paging until `method_name_next()` returns None.

In the following code snippet, the paginated results of a Google Plus activities `list()` method are processed:

```python
activities = service.activities()
request = activities.list(userId='someUserId', collection='public')

while request is not None:
  activities_doc = request.execute(http=http)

  # Do something with the activities

  request = activities.list_next(request, activities_doc)
```

Note that you only call `execute()` on the request once inside the while loop.
