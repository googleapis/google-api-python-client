# version: v1
# title: Command-line sample for the Google URL Shortener API.
# scope: https://www.googleapis.com/auth/urlshortener
# description: Simple command-line example for Google URL Shortener API that shortens a URI then expands it.

  url = service.url()

  # Create a shortened URL by inserting the URL into the url collection.
  body = {"longUrl": "http://code.google.com/apis/urlshortener/" }
  resp = url.insert(body=body).execute()
  pprint.pprint(resp)

  short_url = resp['id']

  # Convert the shortened URL back into a long URL
  resp = url.get(shortUrl=short_url).execute()
  pprint.pprint(resp)
