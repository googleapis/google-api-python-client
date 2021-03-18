# Using OAuth 2.0 for Installed Applications

The Google APIs Client Library for Python supports using OAuth 2.0 in applications that are installed on a device such as a computer, a cell phone, or a tablet. Installed apps are distributed to individual machines, and it is assumed that these apps cannot keep secrets. These apps might access a Google API while the user is present at the app, or when the app is running in the background.

This document is for you if:

- You are writing an installed app for a platform other than Android or iOS, and
- Your installed app will run on devices that have a system browser and rich input capabilities, such as devices with full keyboards.

If you are writing an app for Android or iOS, use [Google Sign-In](https://developers.google.com/identity) to authenticate your users. The Google Sign-In button manages the OAuth 2.0 flow both for authentication and for obtaining authorization to Google APIs. To add the Google Sign-In button, follow the steps for [Android](https://developers.google.com/identity/sign-in/android) or [iOS](https://developers.google.com/identity/sign-in/ios).

If your app will run on devices that do not have access to a system browser, or devices with limited input capabilities (for example, if your app will run on game consoles, video cameras, or printers), then see [Using OAuth 2.0 for Devices](https://developers.google.com/accounts/docs/OAuth2ForDevices).

## Overview

To use OAuth 2.0 in a locally-installed application, first create application credentials for your project in the API Console.

Then, when your application needs to access a user's data with a Google API, your application sends the user to Google's OAuth 2.0 server. The OAuth 2.0 server authenticates the user and obtains consent from the user for your application to access the user's data.

Next, Google's OAuth 2.0 server sends a single-use authorization code to your application, either in the title bar of the browser or in the query string of an HTTP request to the local host. Your application exchanges this authorization code for an access token.

Finally, your application can use the access token to call Google APIs.

This flow is similar to the one shown in the [Using OAuth 2.0 for Web Server Applications](https://developers.google.com/api-client-library/python/auth/web-app), but with three differences:

- When creating a client ID, you specify that your application is an Installed application. This results in a different value for the redirect_uri parameter.
- The client ID and client secret obtained from the API Console are embedded in the source code of your application. In this context, the client secret is obviously not treated as a secret.
- The authorization code can be returned to your application in the title bar of the browser or in the query string of an HTTP request to the local host.

## Creating application credentials

All applications that use OAuth 2.0 must have credentials that identify the application to the OAuth 2.0 server. Applications that have these credentials can access the APIs that you enabled for your project.

To obtain application credentials for your project, complete these steps:

1. Open the [Credentials page](https://console.developers.google.com/apis/credentials) in the API Console.
1. If you haven't done so already, create your OAuth 2.0 credentials by clicking **Create new Client ID** under the **OAuth** heading and selecting the **Installed application** type. Next, look for your application's client ID and client secret in the relevant table.

Download the client_secrets.json file and securely store it in a location that only your application can access.

> **Important:** Do not store the client_secrets.json file in a publicly-accessible location, and if you share the source code to your application—for example, on GitHub—store the client_secrets.json file outside of your source tree to avoid inadvertently sharing your client credentials.

## Configuring the client object

Use the client application credentials that you created to configure a client object in your application. When you configure a client object, you specify the scopes your application needs to access, along with a redirect URI, which will handle the response from the OAuth 2.0 server.

### Choosing a redirect URI

When you create a client ID in the [Google API Console](https://console.developers.google.com/), two redirect_uri parameters are created for you: `urn:ietf:wg:oauth:2.0:oob` and `http://localhost`. The value your application uses determines how the authorization code is returned to your application.

#### http://localhost

This value signals to the Google Authorization Server that the authorization code should be returned as a query string parameter to the web server on the client. You can specify a port number without changing the [Google API Console](https://console.developers.google.com/) configuration. To receive the authorization code using this URI, your application must be listening on the local web server. This is possible on many, but not all, platforms. If your platform supports it, this is the recommended mechanism for obtaining the authorization code.

> **Note:** In some cases, although it is possible to listen, other software (such as a Windows firewall) prevents delivery of the message without significant client configuration.

#### urn:ietf:wg:oauth:2.0:oob

This value signals to the Google Authorization Server that the authorization code should be returned in the title bar of the browser, with the page text prompting the user to copy the code and paste it in the application. This is useful when the client (such as a Windows application) cannot listen on an HTTP port without significant client configuration.

When you use this value, your application can then detect that the page has loaded, and can read the title of the HTML page to obtain the authorization code. It is then up to your application to close the browser window if you want to ensure that the user never sees the page that contains the authorization code. The mechanism for doing this varies from platform to platform.

If your platform doesn't allow you to detect that the page has loaded or read the title of the page, you can have the user paste the code back to your application, as prompted by the text in the confirmation page that the OAuth 2.0 server generates.

#### urn:ietf:wg:oauth:2.0:oob:auto

urn:ietf:wg:oauth:2.0:oob:auto
This is identical to urn:ietf:wg:oauth:2.0:oob, but the text in the confirmation page that the OAuth 2.0 server generates won't instruct the user to copy the authorization code, but instead will simply ask the user to close the window.

This is useful when your application reads the title of the HTML page (by checking window titles on the desktop, for example) to obtain the authorization code, but can't close the page on its own.

### Creating the object

To create a client object from the client_secrets.json file, use the `flow_from_clientsecrets` function. For example, to request read-only access to a user's Google Drive:

```python
from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret.json',
    scopes=['https://www.googleapis.com/auth/drive.metadata.readonly'])
```

Your application uses the client object to perform OAuth 2.0 operations, such as generating authorization request URIs and applying access tokens to HTTP requests.

## Sending users to Google's OAuth 2.0 server

Use either the `run_console` or `run_local_server` function to direct the user to Google's OAuth 2.0 server:

- The run_console function instructs the user to open the authorization URL in their browser. After the user authorizes the application, the authorization server displays a web page with an authorization code, which the user then pastes into the application. The authorization library automatically exchanges the code for an access token.

    ```python
    credentials = flow.run_console()
    ```

- The run_local_server function attempts to open the authorization URL in the user's browser. It also starts a local web server to listen for the authorization response. After the user completes the auth flow, the authorization server redirects the user's browser to the local web server. That server gets the authorization code from the browser and shuts down, then exchanges the code for an access token.

    ```python
    credentials = flow.run_local_server(host='localhost',
        port=8080, 
        authorization_prompt_message='Please visit this URL: {url}', 
        success_message='The auth flow is complete; you may close this window.',
        open_browser=True)
    ```

Google's OAuth 2.0 server authenticates the user and obtains consent from the user for your application to access the requested scopes.

## Calling Google APIs

Use the authorized `Http` object to call Google APIs by completing the following steps:

1. Build a service object for the API that you want to call. You build a a service object by calling the `build` function with the name and version of the API and the authorized Http object. For example, to call version 3 of the Drive API:

    ```python
    from googleapiclient.discovery import build

    drive_service = build('drive', 'v3', credentials=credentials)
    ```

1. Make requests to the API service using the [interface provided by the service object](start.md#build). For example, to list the files in the authenticated user's Google Drive:

    ```python
    files = drive_service.files().list().execute()
    ```

## Complete example

The following example requests access to the user's Google Drive files. If the user grants access, the code retrieves and prints a JSON-formatted list of the five Drive files that were most recently modified by the user.

```python
import os
import pprint

import google.oauth2.credentials

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

pp = pprint.PrettyPrinter(indent=2)

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This access scope grants read-only access to the authenticated user's Drive
# account.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'

def get_authenticated_service():
  flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
  credentials = flow.run_console()
  return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

def list_drive_files(service, **kwargs):
  results = service.files().list(
    **kwargs
  ).execute()

  pp.pprint(results)

if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification. When
  # running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
  service = get_authenticated_service()
  list_drive_files(service,
                   orderBy='modifiedByMeTime desc',
                   pageSize=5)
```
