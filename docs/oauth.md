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

## The `google-auth` and `google-auth-oauthlib` libraries

The [google-auth-oauthlib](https://google-auth-oauthlib.readthedocs.io/en/latest/reference/modules.html) library should be used for handling OAuth 2.0 protocol steps required for making API calls. You should install [google-auth](https://pypi.org/project/google-auth) and [google-auth-oauthlib](https://pypi.org/project/google-auth-oauthlib). The sections below describe important modules, classes, and functions of `google-auth-oauthlib` library.

## Flows

The purpose of a `Flow` class is to acquire credentials that authorize your application access to user data. In order for a user to grant access, OAuth 2.0 steps require your application to potentially redirect their browser multiple times. A `Flow` object has functions that help your application take these steps and acquire credentials. `Flow` objects are only temporary and can be discarded once they have produced credentials, but they can also be [pickled](http://docs.python.org/library/pickle.html) and stored. This section describes the various methods to create and use `Flow` objects.

### Installed App Flow

The [google_auth_oauthlib.flow.InstalledAppFlow](https://google-auth-oauthlib.readthedocs.io/en/latest/reference/google_auth_oauthlib.flow.html#google_auth_oauthlib.flow.InstalledAppFlow) class is used for installed applications. This flow is useful for local development or applications that are installed on a desktop operating system. See [OAuth 2.0 for Installed Applications](oauth-installed.md).

```python
from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secrets.json',
    scopes=['profile', 'email'])

flow.run_local_server()
```

### Flow

The example below uses the `Flow` class to handle the installed application authorization flow.

#### from_client_secrets_file()

The [google_auth_oauthlib.Flow.from_client_secrets()](https://google-auth-oauthlib.readthedocs.io/en/latest/reference/google_auth_oauthlib.flow.html#google_auth_oauthlib.flow.Flow.from_client_secrets_file) method creates a `Flow` object from a [client_secrets.json](client-secrets.md) file. This [JSON](http://www.json.org/) formatted file stores your client ID, client secret, and other OAuth 2.0 parameters.

The following shows how you can use `from_client_secrets_file()` to create a `Flow` object:

```python
from google_auth_oauthlib.flow import Flow
...
flow = Flow.from_client_secrets_file(
    'path/to/client_secrets.json',
    scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
    redirect_uri='urn:ietf:wg:oauth:2.0:oob')
```                               

#### authorization_url()

The [authorization_url()](https://google-auth-oauthlib.readthedocs.io/en/latest/reference/google_auth_oauthlib.flow.html#google_auth_oauthlib.flow.InstalledAppFlow.authorization_url) function of the `Flow` class is used to generate the authorization server URI. Once you have the authorization server URI, redirect the user to it. The following is an example call to this function:

```python
auth_uri = flow.authorization_url()
# Redirect the user to auth_uri on your platform.
```

If the user has previously granted your application access, the authorization server immediately redirects again to `redirect_uri`. If the user has not yet granted access, the authorization server asks them to grant your application access. If they grant access, they get redirected to `redirect_uri` with a `code` query string parameter similar to the following:

`http://example.com/auth_return/?code=kACAH-1Ng1MImB...AA7acjdY9pTD9M`

If they deny access, they get redirected to `redirect_uri` with an `error` query string parameter similar to the following:

`http://example.com/auth_return/?error=access_denied`

#### fetch_token()

The [fetch_token()](https://google-auth-oauthlib.readthedocs.io/en/latest/reference/google_auth_oauthlib.flow.html#google_auth_oauthlib.flow.InstalledAppFlow.fetch_token) function of the `Flow` class exchanges an authorization code for a `Credentials` object. The credentials will be available in `flow.credentials`.

```python
# The user will get an authorization code. This code is used to get the
# access token.
code = input('Enter the authorization code: ')
flow.fetch_token(code=code)
```


## Credentials

A `Credentials` object holds refresh and access tokens that authorize access to a single user's data. These objects are applied to `httplib2.Http` objects to authorize access. They only need to be applied once and can be stored. This section describes the various methods to create and use `Credentials` objects.

**Note**: Credentials can be automatically detected in Google App Engine and Google Compute Engine. See [Using OAuth 2.0 for Server to Server Applications](oauth-server.md#examples).

### User Credentials

The [google.oauth2.credentials.Credentials](https://google-auth.readthedocs.io/en/latest/reference/google.oauth2.credentials.html#google.oauth2.credentials.Credentials) class holds OAuth 2.0 credentials that authorize access to a user's data. A `Flow` object can create one for you.

### Service Account Credentials

The [google.oauth2.service_account.Credentials](https://google-auth.readthedocs.io/en/latest/reference/google.oauth2.service_account.html#google.oauth2.service_account.Credentials) class is only used with [OAuth 2.0 Service Accounts](https://developers.google.com/accounts/docs/OAuth2ServiceAccount). No end-user is involved for these server-to-server API calls, so you can create this object directly.

```python
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    '/path/to/key.json')

scoped_credentials = credentials.with_scopes(
    ['https://www.googleapis.com/auth/cloud-platform'])
```

### Using Credentials

Once a valid credentials object has been obtained it is passed to the build function:

```python
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secrets.json',
    scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'])

flow.run_local_server()
credentials = flow.credentials

service = build('calendar', 'v3', credentials=credentials)

# Optionally, view the email address of the authenticated user.
user_info_service = build('oauth2', 'v2', credentials=credentials)
user_info = user_info_service.userinfo().get().execute()
print(user_info['email'])

```

## Storage

`google-auth-oauthlib` does not currently have support for credentials storage. It may be added in the future. See [oauth2client deprecation](https://google-auth.readthedocs.io/en/latest/oauth2client-deprecation.html#replacement) for more details.

## oauth2client deprecation
The [oauth2client](http://oauth2client.readthedocs.org/en/latest/index.html) library was previously recommended for handling the OAuth 2.0 protocol. It is now deprecated, and we recommend `google-auth` and `google-auth-oauthlib`. See [oauth2client deprecation](https://google-auth.readthedocs.io/en/latest/oauth2client-deprecation.html) for more details.
