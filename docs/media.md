# Media Upload

Some API methods support uploading media files in addition to a regular body. All of these methods have a parameter called `media_body`. For example, if we had a fictional Farm service that allowed managing animals on a farm, the insert method might allow you to upload an image of the animal when adding it to the collection of all animals. The documentation for this method could be:

```py
insert = method(self, **kwargs)
# Adds an animal to the farm.

# Args:
#   body: object, The request body. (required)
#   media_body: string or MediaUpload, Picture of the animal.
```

In the following example, the filename of an image is supplied:

```py
response = farm.animals().insert(media_body='pig.png', body={'name': 'Pig'}).execute()
```

Alternatively, if you want to explicitly control the MIME type of the file sent, use the [googleapiclient.http.MediaFileUpload](https://google.github.io/google-api-python-client/docs/epy/googleapiclient.http.MediaFileUpload-class.html) class for the media_body value:

```py
media = MediaFileUpload('pig.png', mimetype='image/png')
response = farm.animals().insert(media_body=media, body={'name': 'Pig'}).execute()
```

## Resumable media (chunked upload)

For large media files, you can use resumable media uploads to send files, which allows files to be uploaded in smaller chunks. This is especially useful if you are transferring large files, and the likelihood of a network interruption or some other transmission failure is high. It can also reduce your bandwidth usage in the event of network failures because you don't have to restart large file uploads from the beginning.

To use resumable media you must use a MediaFileUpload object and flag it as a resumable upload. You then repeatedly call `next_chunk()` on the [`googleapiclient.http.HttpRequest`](googleapiclient.http.HttpRequest) object until the upload is complete. In the following code, the `status` object reports the progress of the upload, and the response object is created once the upload is complete:

```py
media = MediaFileUpload('pig.png', mimetype='image/png', resumable=True)
request = farm.animals().insert(media_body=media, body={'name': 'Pig'})
response = None
while response is None:
  status, response = request.next_chunk()
  if status:
    print "Uploaded %d%%." % int(status.progress() * 100)
print "Upload Complete!"
```

You can also change the default chunk size by using the `chunksize` parameter:

```py
media = MediaFileUpload('pig.png', mimetype='image/png', chunksize=1048576, resumable=True)
```

> Note: Chunk size restriction: There are some chunk size restrictions based on the size of the file you are uploading. Files larger than 256 KB (256 * 1024 B) must have chunk sizes that are multiples of 256 KB. For files smaller than 256 KB, there are no restrictions. In either case, the final chunk has no limitations; you can simply transfer the remaining bytes.

If a request fails, an [`googleapiclient.errors.HttpError`](https://google.github.io/google-api-python-client/docs/epy/googleapiclient.errors.HttpError-class.html) exception is thrown, which should be caught and handled. If the error is retryable, the upload can be resumed by continuing to call request.next_chunk(), but subsequent calls must use an exponential backoff strategy for retries. The retryable error status codes are:

- 404 Not Found (must restart upload)
- 500 Internal Server Error
- 502 Bad Gateway
- 503 Service Unavailable
- 504 Gateway Timeout

The following is a good exception handling pattern for resumable media uploads:

```py
except apiclient.errors.HttpError, e:
  if e.resp.status in [404]:
    # Start the upload all over again.
  elif e.resp.status in [500, 502, 503, 504]:
    # Call next_chunk() again, but use an exponential backoff for repeated errors.
  else:
    # Do not retry. Log the error and fail.
```

## Extending MediaUpload

Your application may need to upload a media object that isn't a file. For example, you may create a large image on the fly from a data set. For such cases you can create a subclass of [MediaUpload](https://google.github.io/google-api-python-client/docs/epy/googleapiclient.http.MediaUpload-class.html) which provides the data to be uploaded. You must fully implement the MediaUpload interface. See the source for the [MediaFileUpload](https://google.github.io/google-api-python-client/docs/epy/googleapiclient.http.MediaFileUpload-class.html), [MediaIoBaseUpload](MediaIoBaseUpload), and [MediaInMemoryUpload](https://google.github.io/google-api-python-client/docs/epy/googleapiclient.http.MediaInMemoryUpload-class.html) classes as examples.

