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

*   **Scope**: Each API defines one or more scopes that declare a set of operations permitted. For example, an API might have read-only and read-write scopes. When your application requests access to user data, the request must include one or more scopes. The user needs to approve the scope of access your application is requesting. A list of accessible OAuth 2.0 scopes can be [found here](https://developers.google.com/identity/protocols/oauth2/scopes).
*   **Refresh and access tokens**: When a user grants your application access, the OAuth 2.0 authorization server provides your application with refresh and access tokens. These tokens are only valid for the scope requested. Your application uses access tokens to authorize API calls. Access tokens expire, but refresh tokens do not. Your application can use a refresh token to acquire a new access token.

    > **Warning**: Keep refresh and access tokens private. If someone obtains your tokens, they could use them to access private user data.

*   **Client ID and client secret**: These strings uniquely identify your application and are used to acquire tokens. They are created for your Google Cloud project on the [API Access pane](https://console.developers.google.com/apis/credentials) of the Google Cloud. There are several types of client IDs, so be sure to get the correct type for your application:

    *   Web application client IDs
    *   Installed application client IDs
    *   [Service Account](https://developers.google.com/identity/protocols/OAuth2ServiceAccount) client IDs

    > **Warning**: Keep your client secret private. If someone obtains your client secret, they could use it to consume your quota, incur charges against your Google Cloud project, and request access to user data.

## Building and calling a service

This section describes how to build an API-specific service object, make calls to the service, and process the response.

### Build the service object

Whether you are using simple or authorized API access, you use the [build()](http://googleapis.github.io/google-api-python-client/docs/epy/googleapiclient.discovery-module.html#build) function to create a service object. It takes an API name and API version as arguments. You can see the list of all API versions on the [Supported APIs](dyn/index.md) page. When `build()` is called, a service object will attempt to be constructed with methods specific to the given API.

`httplib2`, the underlying transport library, makes all connections persistent by default. Use the service object with a context manager or call `close` to avoid leaving sockets open.


```python
from googleapiclient.discovery import build

service = build('drive', 'v3')
# ...
service.close()
```

```python
from googleapiclient.discovery import build

with build('drive', 'v3') as service:
    # ...
```

**Note**: Under the hood, the `build()` function retrieves a discovery artifact in order to construct the service object.  If the `cache_discovery` argument of `build()` is set to `True`, the library will attempt to retrieve the discovery artifact from the legacy cache which is only supported with `oauth2client<4.0`. If the artifact is not available in the legacy cache and the `static_discovery` argument of `build()` is set to `True`, which is the default, the library will use the service definition shipped in the library. If always using the latest version of a service definition is more important than reliability, users should set `static_discovery=False` to retrieve the service definition from the internet.

### Collections

Each API service provides access to one or more resources. A set of resources of the same type is called a collection. The names of these collections are specific to the API. The service object is constructed with a function for every collection defined by the API. If the given API has a collection named `stamps`, you create the collection object like this:


```python
collection = service.stamps()
```

It is also possible for collections to be nested:


```python
nested_collection = service.featured().stamps()
```

### Methods and requests

Every collection has a list of methods defined by the API. Calling a collection's method returns an [HttpRequest](http://google.github.io/google-api-python-client/docs/epy/googleapiclient.http.HttpRequest-class.html) object. If the given API collection has a method named `list` that takes an argument called `cents`, you create a request object for that method like this:

```python
request = collection.list(cents=5)
```

### Execution and response

Creating a request does not actually call the API. To execute the request and get a response, call the `execute()` function:

```python
try:
    response = request.execute()
except HttpError as e:
    print('Error response status code : {0}, reason : {1}'.format(e.status_code, e.error_details))
```

Alternatively, you can combine previous steps on a single line:

```python
response = service.stamps().list(cents=5).execute()
```

### Working with the response

The response is a Python object built from the JSON response sent by the API server. The JSON structure is specific to the API; for details, see the API's reference documentation. You can also simply print the JSON to see the structure:

```python
import json
...
print(json.dumps(response, sort_keys=True, indent=4))
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

```python
print('Num 5 cent stamps: %d'.format(response['count']))
print('First stamp name: %s'.format(response['items'][0]['name']))
```

## Finding information about the APIs

Use the [APIs Explorer](https://developers.google.com/apis-explorer/) to browse APIs, list available methods, and even try API calls from your browser.

## Library reference documentation

[Core library documentation](http://googleapis.github.io/google-api-python-client/docs/epy/index.html).
and [Library reference documentation by API](dyn/index.md). is available.
