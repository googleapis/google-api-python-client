# OAuth 2.0

This document describes OAuth 2.0, when to use it, how to acquire client IDs, and how to use it with the Google APIs Client Library for Python.

## OAuth 2.0 explained

OAuth 2.0 is the authorization protocol used by Google APIs. It is summarized on the [Authentication](auth.md) page of this library's documentation, and there are other good references as well:

*   [The OAuth 2.0 Authorization Protocol](https://tools.ietf.org/html/rfc6749)
*   [Using OAuth 2.0 to Access Google APIs](https://developers.google.com/accounts/docs/OAuth2)

The protocol is solving a complex problem, so it can be difficult to understand. This presentation explains the important concepts of the protocol, and introduces you to how the library is used at each step.

## Acquiring client IDs and secrets

You can get client IDs and secrets on the [API Access pane](https://console.developers.google.com/apis/credentials) of the Google APIs Console. There are different types of client IDs, so be sure to get the correct type for your application:

*   Web application client IDs
*   Installed application client IDs
*   [Service Account](https://developers.google.com/accounts/docs/OAuth2ServiceAccount) client IDs

**Warning**: Keep your client secret private. If someone obtains your client secret, they could use it to consume your quota, incur charges against your Google APIs Console project, and request access to user data.

## The oauth2client library

The [oauth2client](http://oauth2client.readthedocs.org/en/latest/index.html) library is included with the Google APIs Client Library for Python. It handles all steps of the OAuth 2.0 protocol required for making API calls. It is available as a separate [package](https://pypi.python.org/pypi/oauth2client) if you only need an OAuth 2.0 library. The sections below describe important modules, classes, and functions of this library.

## Flows

The purpose of a `Flow` class is to acquire credentials that authorize your application access to user data. In order for a user to grant access, OAuth 2.0 steps require your application to potentially redirect their browser multiple times. A `Flow` object has functions that help your application take these steps and acquire credentials. `Flow` objects are only temporary and can be discarded once they have produced credentials, but they can also be [pickled](http://docs.python.org/library/pickle.html) and stored. This section describes the various methods to create and use `Flow` objects.

**Note**: See the [Using Google App Engine](app-engine.md) and [Using Django](django.md) pages for platform-specific Flows.

### flow_from_clientsecrets()

The [oauth2client.client.flow_from_clientsecrets()](http://oauth2client.readthedocs.org/en/latest/source/oauth2client.client.html#oauth2client.client.flow_from_clientsecrets) method creates a `Flow` object from a [client_secrets.json](client_secrets.md) file. This [JSON](http://www.json.org/) formatted file stores your client ID, client secret, and other OAuth 2.0 parameters.

The following shows how you can use `flow_from_clientsecrets()` to create a `Flow` object:

```py
from oauth2client.client import flow_from_clientsecrets
...
flow = flow_from_clientsecrets('path_to_directory/client_secrets.json',
                               scope='https://www.googleapis.com/auth/calendar',
                               redirect_uri='http://example.com/auth_return')
```                               

### OAuth2WebServerFlow

Despite its name, the [oauth2client.client.OAuth2WebServerFlow](http://oauth2client.readthedocs.org/en/latest/source/oauth2client.client.html#oauth2client.client.OAuth2WebServerFlow) class is used for both installed and web applications. It is created by passing the client ID, client secret, and scope to its constructor: You provide the constructor with a `redirect_uri` parameter. This must be a URI handled by your application.

```py
from oauth2client.client import OAuth2WebServerFlow
...
flow = OAuth2WebServerFlow(client_id='your_client_id',
                           client_secret='your_client_secret',
                           scope='https://www.googleapis.com/auth/calendar',
                           redirect_uri='http://example.com/auth_return')
```

### step1_get_authorize_url()

The [step1_get_authorize_url()](http://oauth2client.readthedocs.org/en/latest/source/oauth2client.client.html#oauth2client.client.OAuth2WebServerFlow.step1_get_authorize_url) function of the `Flow` class is used to generate the authorization server URI. Once you have the authorization server URI, redirect the user to it. The following is an example call to this function:

```py
auth_uri = flow.step1_get_authorize_url()
# Redirect the user to auth_uri on your platform.
```

If the user has previously granted your application access, the authorization server immediately redirects again to `redirect_uri`. If the user has not yet granted access, the authorization server asks them to grant your application access. If they grant access, they get redirected to `redirect_uri` with a `code` query string parameter similar to the following:

`http://example.com/auth_return/?code=kACAH-1Ng1MImB...AA7acjdY9pTD9M`

If they deny access, they get redirected to `redirect_uri` with an `error` query string parameter similar to the following:

`http://example.com/auth_return/?error=access_denied`

### step2_exchange()

The [step2_exchange()](http://oauth2client.readthedocs.org/en/latest/source/oauth2client.client.html#oauth2client.client.OAuth2WebServerFlow.step2_exchange) function of the `Flow` class exchanges an authorization code for a `Credentials` object. Pass the `code` provided by the authorization server redirection to this function:

```py
credentials = flow.step2_exchange(code)
```

## Credentials

A `Credentials` object holds refresh and access tokens that authorize access to a single user's data. These objects are applied to `httplib2.Http` objects to authorize access. They only need to be applied once and can be stored. This section describes the various methods to create and use `Credentials` objects.

**Note**: See the [Using Google App Engine](google-app-engine.md) and [Using Django](django.md) pages for platform-specific Credentials.

### OAuth2Credentials

The [oauth2client.client.OAuth2Credentials](http://oauth2client.readthedocs.org/en/latest/source/oauth2client.client.html#oauth2client.client.OAuth2Credentials) class holds OAuth 2.0 credentials that authorize access to a user's data. Normally, you do not create this object by calling its constructor. A `Flow` object can create one for you.

### ServiceAccountCredentials

The [oauth2client.service_account.ServiceAccountCredentials](http://oauth2client.readthedocs.org/en/latest/source/oauth2client.service_account.html) class is only used with [OAuth 2.0 Service Accounts](https://developers.google.com/accounts/docs/OAuth2ServiceAccount). No end-user is involved for these server-to-server API calls, so you can create this object directly without using a `Flow` object.

### AccessTokenCredentials

The [oauth2client.client.AccessTokenCredentials](http://oauth2client.readthedocs.org/en/latest/source/oauth2client.client.html#oauth2client.client.AccessTokenCredentials) class is used when you have already obtained an access token by some other means. You can create this object directly without using a `Flow` object.

### authorize()

Use the [authorize()](http://oauth2client.readthedocs.org/en/latest/source/oauth2client.client.html#oauth2client.client.Credentials.authorize) function of the `Credentials` class to apply necessary credential headers to all requests made by an [httplib2.Http](http://bitworking.org/projects/httplib2/doc/html/libhttplib2.html#httplib2.Http) instance:

```py
import httplib2
...
http = httplib2.Http()
http = credentials.authorize(http)
```

Once an `httplib2.Http` object has been authorized, it is typically passed to the build function:

```py
from apiclient.discovery import build
...
service = build('calendar', 'v3', http=http)
```

## Storage

A [oauth2client.client.Storage](http://oauth2client.readthedocs.org/en/latest/source/oauth2client.client.html#oauth2client.client.Storage) object stores and retrieves `Credentials` objects. This section describes the various methods to create and use `Storage` objects.

**Note**: See the [Using Google App Engine](app-engine.md) and [Using Django](django.md) pages for platform-specific Storage.

### file.Storage

The [oauth2client.file.Storage](http://oauth2client.readthedocs.org/en/latest/source/oauth2client.file.html#oauth2client.file.Storage) class stores and retrieves a single `Credentials` object. The class supports locking such that multiple processes and threads can operate on a single store. The following shows how to open a file, save `Credentials` to it, and retrieve those credentials:

```py
from oauth2client.file import Storage
...
storage = Storage('_a_credentials_file_')
storage.put(credentials)
...
credentials = storage.get()
```

### multistore_file

The [oauth2client.contrib.multistore_file](http://oauth2client.readthedocs.org/en/latest/source/oauth2client.contrib.multistore_file.html) module allows multiple credentials to be stored. The credentials are keyed off of:

*   client ID
*   user agent
*   scope

### keyring_storage

The [oauth2client.contrib.keyring_storage](http://oauth2client.readthedocs.org/en/latest/source/oauth2client.contrib.keyring_storage.html) module allows a single `Credentials` object to be stored in a [password manager](http://en.wikipedia.org/wiki/Password_manager) if one is available. The credentials are keyed off of:

*   Name of the client application
*   User name

```py
from oauth2client.contrib.keyring_storage import Storage
...
storage = Storage('_application name_', '_user name_')
storage.put(credentials)
...
credentials = storage.get()
```

## Command-line tools

The [oauth2client.tools.run_flow()](http://oauth2client.readthedocs.org/en/latest/source/oauth2client.tools.html#oauth2client.tools.run_flow) function can be used by command-line applications to acquire credentials. It takes a `Flow` argument and attempts to open an authorization server page in the user's default web browser. The server asks the user to grant your application access to the user's data. If the user grants access, the run() function returns new credentials. The new credentials are also stored in the `Storage` argument, which updates the file associated with the `Storage` object.

The [oauth2client.tools.run_flow()](http://oauth2client.readthedocs.org/en/latest/source/oauth2client.tools.html#oauth2client.tools.run_flow) function is controlled by command-line flags, and the Python standard library [argparse](http://docs.python.org/dev/library/argparse.html) module must be initialized at the start of your program. Argparse is included in Python 2.7+, and is available as a [separate package](https://pypi.python.org/pypi/argparse) for older versions. The following shows an example of how to use this function:

```py
import argparse
from oauth2client import tools

parser = argparse.ArgumentParser(parents=[tools.argparser])
flags = parser.parse_args()
...
credentials = tools.run_flow(flow, storage, flags)
```