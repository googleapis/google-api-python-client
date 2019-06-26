# Using Google App Engine

The Google APIs Client Library for Python has special support for [Google App Engine](https://developers.google.com/appengine) applications. In particular, there are decorators and classes that simplify the OAuth 2.0 protocol steps. Before reading this page, you should be familiar with the content on this library's [OAuth 2.0](https://developers.google.com/api-client-library/python/guide/aaa_oauth) page.

## Decorators

The easiest way to handle OAuth 2.0 is to use the App Engine [Python decorators](http://en.wikipedia.org/wiki/Python_syntax_and_semantics#Decorators) supplied by this library. These decorators handle all of the OAuth 2.0 steps without you having to use any `Flow`, `Credentials`, or `Storage` objects.

There are two decorator classes to choose from:

*   **OAuth2Decorator**: Use the [OAuth2Decorator](https://oauth2client.readthedocs.io/en/latest/source/oauth2client.contrib.appengine.html#oauth2client.contrib.appengine.OAuth2Decorator) class to contruct a decorator with your client ID and secret.
*   **OAuth2DecoratorFromClientSecrets**: Use the [OAuth2DecoratorFromClientSecrets](https://oauth2client.readthedocs.io/en/latest/source/oauth2client.contrib.appengine.html#oauth2client.contrib.appengine.OAuth2DecoratorFromClientSecrets) class to contruct a decorator using a `client_secrets.json` file described in the [flow\_from\_clientsecrets()](https://developers.google.com/api-client-library/python/guide/aaa_oauth#flow_from_clientsecrets) section of the OAuth 2.0 page.

There are also two decorator types to choose from:

*   **oauth\_required**: Any method decorated with `oauth_required` completes all OAuth 2.0 steps before entering the function. Within the body of the function, you can use the decorator's `http()` function to get an `Http` object that has already been authorized.
*   **oauth\_aware**: This decorator type requires a little more code than `oauth_required`, but it is preferred because it gives you control over the user experience. For example, you can display a page explaining why the user is being redirected to an authorization server. This decorator does not perform any OAuth 2.0 steps, but within the body of the decorated function you can call these convenient decorator functions:
    *   **has\_credentials()**: Returns `True` if there are valid access credentials for the logged in user.
    *   **authorize\_url()**: Returns the first URL that starts the OAuth 2.0 steps.

When using these decorators, you need to add a specific URL handler to your application to handle the redirection from the authorization server back to your application. This handler takes care of the final OAuth 2.0 steps required to finish authorization, and it redirects the user back to the original path where your application first detected that authorization was needed.

```py
def main():
  application = webapp.WSGIApplication(
    [
      ('/', MainHandler),
      ('/about', AboutHandler),
      (decorator.callback_path, decorator.callback_handler()),
    ],
    debug=True)
  run_wsgi_app(application)
```

In the following code snippet, the `OAuth2Decorator` class is used to create an `oauth_required` decorator, and the decorator is applied to a function that accesses the [Google Calendar API](https://developers.google.com/google-apps/calendar/):

```py
from apiclient.discovery import build
from google.appengine.ext import webapp
from oauth2client.contrib.appengine import OAuth2Decorator

decorator = OAuth2Decorator(
  client_id='your_client_id',
  client_secret='your_client_secret',
  scope='https://www.googleapis.com/auth/calendar')

service = build('calendar', 'v3')

class MainHandler(webapp.RequestHandler):

  @decorator.oauth_required
  def get(self):
    # Get the authorized Http object created by the decorator.
    http = decorator.http()
    # Call the service using the authorized Http object.
    request = service.events().list(calendarId='primary')
    response = request.execute(http=http)
    ...
```

In the following code snippet, the `OAuth2DecoratorFromClientSecrets` class is used to create an `oauth_aware` decorator, and the decorator is applied to a function that accesses the [Google Tasks API](https://developers.google.com/google-apps/tasks/):

```py
import os
from apiclient.discovery import build
from google.appengine.ext import webapp
from oauth2client.contrib.appengine import OAuth2DecoratorFromClientSecrets

decorator = OAuth2DecoratorFromClientSecrets(
  os.path.join(os.path.dirname(__file__), 'client_secrets.json'),
  'https://www.googleapis.com/auth/tasks.readonly')

service = build('tasks', 'v1')

class MainHandler(webapp.RequestHandler):

  @decorator.oauth_aware
  def get(self):
    if decorator.has_credentials():
      response = service.tasks().list(tasklist='@default').execute(decorator.http())
      # Write the task data
      ...
    else:
      url = decorator.authorize_url()
      # Write a page explaining why authorization is needed,
      # and provide the user with a link to the url to proceed.
      # When the user authorizes, they get redirected back to this path,
      # and has_credentials() returns True.
      ...
```

## Service Accounts

If your App Engine application needs to call an API to access data owned by the application's project, you can simplify OAuth 2.0 by using [Service Accounts](https://developers.google.com/accounts/docs/OAuth2ServiceAccount). These server-to-server interactions do not involve a user, and only your application needs to authenticate itself. Use the [AppAssertionCredentials](https://oauth2client.readthedocs.io/en/latest/source/oauth2client.contrib.appengine.html#oauth2client.contrib.appengine.AppAssertionCredentials) class to create a `Credentials` object without using a `Flow` object.

In the following code snippet, a `Credentials` object is created and an `Http` object is authorized:

import httplib2from google.appengine.api import memcachefrom oauth2client.contrib.appengine import  AppAssertionCredentials  
...credentials \=  AppAssertionCredentials(scope\='https://www.googleapis.com/auth/devstorage.read\_write')http \= credentials.authorize(httplib2.Http(memcache))

Once you have an authorized `Http` object, you can pass it to the [build()](https://google.github.io/google-api-python-client/docs/epy/googleapiclient.discovery-module.html#build) or [execute()](https://google.github.io/google-api-python-client/docs/epy/googleapiclient.http.HttpRequest-class.html#execute) functions as you normally would.

## Flows

Use App Engine's [Memcache](https://developers.google.com/appengine/docs/python/memcache/usingmemcache) to store `Flow` objects. When your application is simultaneously going through OAuth 2.0 steps for many users, it's normally best to store per-user `Flow` objects before the first redirection. This way, your redirection handlers can retrieve the `Flow` object already created for the user. In the following code snippet, `Memcache` is used to store and retrieve `Flow` objects keyed by user ID:

```py
import pickle
from google.appengine.api import memcache
from google.appengine.api import users
from oauth2client.client import OAuth2WebServerFlow
...
flow = OAuth2WebServerFlow(...)
user = users.get_current_user()
memcache.set(user.user_id(), pickle.dumps(flow))
...
flow = pickle.loads(memcache.get(user.user_id()))
```

## Credentials

Use the [oauth2client.contrib.appengine.CredentialsProperty](https://oauth2client.readthedocs.io/en/latest/source/oauth2client.contrib.appengine.html#oauth2client.contrib.appengine.CredentialsProperty) class as an [App Engine Datastore](https://developers.google.com/appengine/docs/python/datastore/overview) `Property`. Creating a `Model` with this `Property` simplifies storing `Credentials` as explained in the [Storage](#Storage) section below. In the following code snippet, a `Model` class is defined using this `Property`.

```py
from google.appengine.ext import db
from oauth2client.contrib.appengine import CredentialsProperty
...
class CredentialsModel(db.Model):
  credentials = CredentialsProperty()
```

## Storage

Use the [oauth2client.contrib.appengine.StorageByKeyName](https://oauth2client.readthedocs.io/en/latest/source/oauth2client.contrib.appengine.html#oauth2client.contrib.appengine.StorageByKeyName) class to store and retrieve `Credentials` objects to and from the [App Engine Datastore](https://developers.google.com/appengine/docs/python/datastore/overview). You pass the model, key value, and property name to its constructor. The following shows how to create, read, and write `Credentials` objects using the example `CredentialsModel` class above:

```py
from google.appengine.api import users
from oauth2client.contrib.appengine import StorageByKeyName
...
user = users.get_current_user()
storage = StorageByKeyName(CredentialsModel, user.user_id(), 'credentials')
credentials = storage.get()
...
storage.put(credentials)
```

## Samples

To see how these classes work together in a full application, see the [App Engine sample applications](https://github.com/google/google-api-python-client/tree/master/samples/appengine) section of this library’s open source project page.