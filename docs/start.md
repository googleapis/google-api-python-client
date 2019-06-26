# Getting Started

This document provides all the basic information you need to start using the library. It covers important library concepts, shows examples for various use cases, and gives links to more information.

## Setup

There are a few setup steps you need to complete before you can use this library:

1.  If you don't already have a Google account, [sign up](https://www.google.com/accounts).
2.  If you have never created a Google APIs Console project, read the [Managing Projects page](http://developers.google.com/console/help/managing-projects) and create a project in the [Google API Console](https://console.developers.google.com/).
3.  [Install](http://developers.google.com/api-client-library/python/start/installation) the library.

## Authentication and authorization

It is important to understand the basics of how API authentication and authorization are handled. All API calls must use either simple or authorized access (defined below). Many API methods require authorized access, but some can use either. Some API methods that can use either behave differently, depending on whether you use simple or authorized access. See the API's method documentation to determine the appropriate access type.

### 1. Simple API access (API keys)

These API calls do not access any private user data. Your application must authenticate itself as an application belonging to your Google Cloud project. This is needed to measure project usage for accounting purposes.

**API key**: To authenticate your application, use an [API key](https://cloud.google.com/docs/authentication/api-keys) for your Google Cloud Console project. Every simple access call your application makes must include this key.
    
> **Warning**: Keep your API key private. If someone obtains your key, they could use it to consume your quota or incur charges against your Google Cloud project.
    
### 2. Authorized API access (OAuth 2.0)

These API calls access private user data. Before you can call them, the user that has access to the private data must grant your application access. Therefore, your application must be authenticated, the user must grant access for your application, and the user must be authenticated in order to grant that access. All of this is accomplished with [OAuth 2.0](https://developers.google.com/identity/protocols/OAuth2) and libraries written for it.

*   **Scope**: Each API defines one or more scopes that declare a set of operations permitted. For example, an API might have read-only and read-write scopes. When your application requests access to user data, the request must include one or more scopes. The user needs to approve the scope of access your application is requesting.
*   **Refresh and access tokens**: When a user grants your application access, the OAuth 2.0 authorization server provides your application with refresh and access tokens. These tokens are only valid for the scope requested. Your application uses access tokens to authorize API calls. Access tokens expire, but refresh tokens do not. Your application can use a refresh token to acquire a new access token.
    
    > **Warning**: Keep refresh and access tokens private. If someone obtains your tokens, they could use them to access private user data.
    
*   **Client ID and client secret**: These strings uniquely identify your application and are used to acquire tokens. They are created for your Google Cloud project on the [API Access pane](https://code.google.com/apis/console#:access) of the Google Cloud. There are three types of client IDs, so be sure to get the correct type for your application:
    
    *   Web application client IDs
    *   Installed application client IDs
    *   [Service Account](https://developers.google.com/identity/protocols/OAuth2ServiceAccount) client IDs
    
    > **Warning**: Keep your client secret private. If someone obtains your client secret, they could use it to consume your quota, incur charges against your Google Cloud project, and request access to user data.

## Building and calling a service

This section describes how to build an API-specific service object, make calls to the service, and process the response.

### Build the service object

Whether you are using simple or authorized API access, you use the [build()](http://google.github.io/google-api-python-client/docs/epy/googleapiclient.discovery-module.html#build) function to create a service object. It takes an API name and API version as arguments. You can see the list of all API versions on the [Supported APIs](http://developers.google.com/api-client-library/python/apis/) page. The service object is constructed with methods specific to the given API. To create it, do the following:

```py
from apiclient.discovery import build
service = build('api_name', 'api_version', ...)
```

### Collections

Each API service provides access to one or more resources. A set of resources of the same type is called a collection. The names of these collections are specific to the API. The service object is constructed with a function for every collection defined by the API. If the given API has a collection named `stamps`, you create the collection object like this:

```py
collection = service.stamps()
```

It is also possible for collections to be nested:

```py
nested_collection = service.featured().stamps()
```

### Methods and requests

Every collection has a list of methods defined by the API. Calling a collection's method returns an [HttpRequest](http://google.github.io/google-api-python-client/docs/epy/googleapiclient.http.HttpRequest-class.html) object. If the given API collection has a method named `list` that takes an argument called `cents`, you create a request object for that method like this:

```py
request = collection.list(cents=5)
```

### Execution and response

Creating a request does not actually call the API. To execute the request and get a response, call the `execute()` function:

```py
response = request.execute()
```

Alternatively, you can combine previous steps on a single line:

```py
response = service.stamps().list(cents=5).execute()
```

### Working with the response

The response is a Python object built from the JSON response sent by the API server. The JSON structure is specific to the API; for details, see the API's reference documentation. You can also simply print the JSON to see the structure:

```py
import json
...
print json.dumps(response, sort_keys=True, indent=4)
```

For example, if the printed JSON is the following:

```json
{
    "count": 2,
    "items": [
        {
            "cents": 5,
            "name": "#586 1923-26 5-cent blue Theodore Roosevelt MLH perf 10"
        },
        {
            "cents": 5,
            "name": "#628 1926 5-cent Ericsson Memorial MLH"
        }
    ]
}
```

You can access the data like this:

```py
print 'Num 5 cent stamps: %d' % response['count']
print 'First stamp name: %s' % response['items'][0]['name']
```

## Examples

In this section, we provide examples of each access type and application type.

### Authorized API for web application example

For this example, we use authorized API access for a simple web server. It calls the [Google Calendar API](http://developers.google.com/google-apps/calendar/) to list a user's calendar events. Python's built-in [BaseHTTPServer](http://docs.python.org/2/library/basehttpserver.html) is used to create the server. Actual production code would normally use a more sophisticated web server framework, but the simplicity of `BaseHTTPServer` allows the example to focus on using this library.

#### Setup for example

1.  **Activate the Calendar API**: [Read about API activation](http://developers.google.com/console/help/activating-apis) and activate the Calendar API.
2.  **Get your client ID and client secret**: Get a client ID and secret for _web applications_. Use `http://localhost` as your domain. After creating the client ID, edit the _Redirect URIs_ field to contain only `http://localhost:8080/`.
3.  **Create calendar events**: In this example, user calendar events will be read. You can use any Google account you own, including the account associated with the application's Google APIs Console project. For the target user, create a few calendar events if none exist already.

#### Code for example

This script is well commented to explain each step.

```py
#!/usr/bin/python
import BaseHTTPServer
import Cookie
import httplib2
import StringIO
import urlparse
import sys

from apiclient.discovery import build
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  """Child class of BaseHTTPRequestHandler that only handles GET request."""

  # Create a flow object. This object holds the client_id, client_secret, and
  # scope. It assists with OAuth 2.0 steps to get user authorization and
  # credentials. For this example, the client ID and secret are command-line
  # arguments.
  flow = OAuth2WebServerFlow(sys.argv[1],
                             sys.argv[2],
                             'https://www.googleapis.com/auth/calendar',
                             redirect_uri='http://localhost:8080/')

  def do_GET(self):
    """Handler for GET request."""
    print '\nNEW REQUEST, Path: %s' % (self.path)
    print 'Headers: %s' % self.headers

    # To use this server, you first visit
    # http://localhost:8080/?fake_user=<some_user_name>. You can use any name you
    # like for the fake_user. It's only used as a key to store credentials,
    # and has no relationship with real user names. In a real system, you would
    # only use logged-in users for your system.
    if self.path.startswith('/?fake_user='):
      # Initial page entered by user
      self.handle_initial_url()

    # When you redirect to the authorization server below, it redirects back
    # to to http://localhost:8080/?code=<some_code> after the user grants access
    # permission for your application.
    elif self.path.startswith('/?code='):
      # Page redirected back from auth server
      self.handle_redirected_url()
    # Only the two URL patterns above are accepted by this server.
    else:
      # Either an error from auth server or bad user entered URL.
      self.respond_ignore()

  def handle_initial_url(self):
    """Handles the initial path."""
    # The fake user name should be in the URL query parameters.
    fake_user = self.get_fake_user_from_url_param()

    # Call a helper function defined below to get the credentials for this user.
    credentials = self.get_credentials(fake_user)

    # If there are no credentials for this fake user or they are invalid,
    # we need to get new credentials.
    if credentials is None or credentials.invalid:
      # Call a helper function defined below to respond to this GET request
      # with a response that redirects the browser to the authorization server.
      self.respond_redirect_to_auth_server(fake_user)
    else:
      try:
        # Call a helper function defined below to get calendar data for this
        # user.
        calendar_output = self.get_calendar_data(credentials)

        # Call a helper function defined below which responds to this
        # GET request with data from the calendar.
        self.respond_calendar_data(calendar_output)
      except AccessTokenRefreshError:
        # This may happen when access tokens expire. Redirect the browser to
        # the authorization server
        self.respond_redirect_to_auth_server(fake_user)

  def handle_redirected_url(self):
    """Handles the redirection back from the authorization server."""
    # The server should have responded with a "code" URL query parameter. This
    # is needed to acquire credentials.
    code = self.get_code_from_url_param()

    # Before we redirected to the authorization server, we set a cookie to save
    # the fake user for retrieval when handling the redirection back to this
    # server. This is only needed because we are using this fake user
    # name as a key to access credentials.
    fake_user = self.get_fake_user_from_cookie()

    #
    # This is an important step.
    #
    # We take the code provided by the authorization server and pass it to the
    # flow.step2_exchange() function. This function contacts the authorization
    # server and exchanges the "code" for credentials.
    credentials = RequestHandler.flow.step2_exchange(code)

    # Call a helper function defined below to save these credentials.
    self.save_credentials(fake_user, credentials)

    # Call a helper function defined below to get calendar data for this user.
    calendar_output = self.get_calendar_data(credentials)

    # Call a helper function defined below which responds to this GET request
    # with data from the calendar.
    self.respond_calendar_data(calendar_output)

  def respond_redirect_to_auth_server(self, fake_user):
    """Respond to the current request by redirecting to the auth server."""
    #
    # This is an important step.
    #
    # We use the flow object to get an authorization server URL that we should
    # redirect the browser to. We also supply the function with a redirect_uri.
    # When the auth server has finished requesting access, it redirects
    # back to this address. Here is pseudocode describing what the auth server
    # does:
    #   if (user has already granted access):
    #     Do not ask the user again.
    #     Redirect back to redirect_uri with an authorization code.
    #   else:
    #     Ask the user to grant your app access to the scope and service.
    #     if (the user accepts):
    #       Redirect back to redirect_uri with an authorization code.
    #     else:
    #       Redirect back to redirect_uri with an error code.
    uri = RequestHandler.flow.step1_get_authorize_url()

    # Set the necessary headers to respond with the redirect. Also set a cookie
    # to store our fake_user name. We will need this when the auth server
    # redirects back to this server.
    print 'Redirecting %s to %s' % (fake_user, uri)
    self.send_response(301)
    self.send_header('Cache-Control', 'no-cache')
    self.send_header('Location', uri)
    self.send_header('Set-Cookie', 'fake_user=%s' % fake_user)
    self.end_headers()

  def respond_ignore(self):
    """Responds to the current request that has an unknown path."""
    self.send_response(200)
    self.send_header('Content-type', 'text/plain')
    self.send_header('Cache-Control', 'no-cache')
    self.end_headers()
    self.wfile.write(
      'This path is invalid or user denied access:\n%s\n\n' % self.path)
    self.wfile.write(
      'User entered URL should look like: http://localhost:8080/?fake_user=johndoe')

  def respond_calendar_data(self, calendar_output):
    """Responds to the current request by writing calendar data to stream."""
    self.send_response(200)
    self.send_header('Content-type', 'text/plain')
    self.send_header('Cache-Control', 'no-cache')
    self.end_headers()
    self.wfile.write(calendar_output)

  def get_calendar_data(self, credentials):
    """Given the credentials, returns calendar data."""
    output = StringIO.StringIO()

    # Now that we have credentials, calling the API is very similar to
    # other authorized access examples.

    # Create an httplib2.Http object to handle our HTTP requests, and authorize
    # it using the credentials.authorize() function.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # The apiclient.discovery.build() function returns an instance of an API
    # service object that can be used to make API calls.
    # The object is constructed with methods specific to the calendar API.
    # The arguments provided are:
    #   name of the API ('calendar')
    #   version of the API you are using ('v3')
    #   authorized httplib2.Http() object that can be used for API calls
    service = build('calendar', 'v3', http=http)

    # The Calendar API's events().list method returns paginated results, so we
    # have to execute the request in a paging loop. First, build the request
    # object. The arguments provided are:
    #   primary calendar for user
    request = service.events().list(calendarId='primary')
    # Loop until all pages have been processed.
    while request != None:
      # Get the next page.
      response = request.execute()
      # Accessing the response like a dict object with an 'items' key
      # returns a list of item objects (events).
      for event in response.get('items', []):
        # The event object is a dict object with a 'summary' key.
        output.write(repr(event.get('summary', 'NO SUMMARY')) + '\n')
      # Get the next request object by passing the previous request object to
      # the list_next method.
      request = service.events().list_next(request, response)

    # Return the string of calendar data.
    return output.getvalue()

  def get_credentials(self, fake_user):
    """Using the fake user name as a key, retrieve the credentials."""
    storage = Storage('credentials-%s.dat' % (fake_user))
    return storage.get()

  def save_credentials(self, fake_user, credentials):
    """Using the fake user name as a key, save the credentials."""
    storage = Storage('credentials-%s.dat' % (fake_user))
    storage.put(credentials)

  def get_fake_user_from_url_param(self):
    """Get the fake_user query parameter from the current request."""
    parsed = urlparse.urlparse(self.path)
    fake_user = urlparse.parse_qs(parsed.query)['fake_user'][0]
    print 'Fake user from URL: %s' % fake_user
    return fake_user

  def get_fake_user_from_cookie(self):
    """Get the fake_user from cookies."""
    cookies = Cookie.SimpleCookie()
    cookies.load(self.headers.get('Cookie'))
    fake_user = cookies['fake_user'].value
    print 'Fake user from cookie: %s' % fake_user
    return fake_user

  def get_code_from_url_param(self):
    """Get the code query parameter from the current request."""
    parsed = urlparse.urlparse(self.path)
    code = urlparse.parse_qs(parsed.query)['code'][0]
    print 'Code from URL: %s' % code
    return code

def main():
  try:
    server = BaseHTTPServer.HTTPServer(('', 8080), RequestHandler)
    print 'Starting server. Use Control+C to stop.'
    server.serve_forever()
  except KeyboardInterrupt:
    print 'Shutting down server.'
    server.socket.close()

if __name__ == '__main__':
  main()
```

Note how the Storage object is used to to retrieve and store credentials. If no credentials are found, the `flow.step1_get_authorize_url()` function is used to redirect the user to the authorization server. Once the user has granted access, the authorization server redirects back to the local server with a `code` query parameter. This code is passed to the `flow.step2_exchange()` function, which returns credentials. From that point forward, this script is very similar to the command-line access example above.

#### Run the example

1.  Copy the script to an **empty** directory on your computer.
2.  Open a terminal and go to the directory.
3.  Execute the following command to run the local server:
    
    python authorized_api_web_server_calendar.py your_client_id your_client_secret
    
4.  Open a web browser and log in to your Google account as the target user.
5.  Go to this URL: `http://localhost:8080/?fake_user=target_user_name` replacing `target_user_name` with the user name for the target user.
6.  If this is the first time the target user has accessed this local server, the target user is redirected to the authorization server. The authorization server asks the target user to grant the application access to calendar data. Click the button that allows access.
7.  The authorization server redirects the browser back to the local server.
8.  Calendar events for the target user are listed on the page.

## Django support

This library includes helper classes that simplify use in a [Django](https://www.djangoproject.com/) application. See the [Using Django](http://developers.google.com/api-client-library/python/guide/django) page for details.

## Google App Engine support

This library includes helper classes that simplify use in a [Google App Engine](http://developers.google.com/appengine/) application. See the [Using Google App Engine](http://developers.google.com/api-client-library/python/guide/google_app_engine) page for details.

## Finding information about the APIs

Use the [APIs Explorer](http://developers.google.com/api-client-library/python/reference/apis_explorer) to browse APIs, list available methods, and even try API calls from your browser.

## Library reference documentation

[PyDoc generated documentation](http://developers.google.com/api-client-library/python/reference/pydoc) is available for all modules in this library.

You can get [interactive help](http://developers.google.com/api-client-library/python/reference/interactive_help) on library classes and functions using an interactive Python shell.