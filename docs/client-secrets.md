# Client Secrets

The Google APIs Client Library for Python uses the `client_secrets.json` file format for storing the `client_id`, `client_secret`, and other OAuth 2.0 parameters.

The `client_secrets.json` file format is a [JSON](http://www.json.org/) formatted file containing the client ID, client secret, and other OAuth 2.0 parameters. Here is an example client_secrets.json file for a web application:

```json
{
  "web": {
    "client_id": "asdfjasdljfasdkjf",
    "client_secret": "1912308409123890",
    "redirect_uris": ["https://www.example.com/oauth2callback"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://accounts.google.com/o/oauth2/token"
  }
}
```

Here is an example client_secrets.json file for an installed application:

```json
{
  "installed": {
    "client_id": "837647042410-75ifg...usercontent.com",
    "client_secret":"asdlkfjaskd",
    "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://accounts.google.com/o/oauth2/token"
  }
}
```

The format defines one of two client ID types:

- `web`: Web application.
- `installed`: Installed application.

The `web` and `installed` sub-objects have the following mandatory members:

- `client_id` (string): The client ID.
- `client_secret` (string): The client secret.
- `redirect_uris` (list of strings): A list of valid redirection endpoint URIs. This list should match the list entered for the client ID on the [API Access pane](https://code.google.com/apis/console#:access) of the Google APIs Console.
- `auth_uri` (string): The authorization server endpoint URI.
- `token_uri` (string): The token server endpoint URI.

All of the above members are mandatory. The following optional parameters may appear:

- `client_email` (string) The service account email associated with the client.
- `auth_provider_x509_cert_url` (string) The URL of the public x509 certificate, used to verify the signature on JWTs, such as ID tokens, signed by the authentication provider.
- `client_x509_cert_url` (string) The URL of the public x509 certificate, used to verify JWTs signed by the client.

The following examples show how use a `client_secrets.json` file to create a `Flow` object in either an installed application or a web application:

### Installed App

```py
from google_auth_oauthlib.flow import InstalledAppFlow
...
flow = InstalledAppFlow.from_client_secrets_file(
    'path_to_directory/client_secret.json',
    scopes=['https://www.googleapis.com/auth/calendar'])
```

### Web Server App

```py
import google.oauth2.credentials
import google_auth_oauthlib.flow

flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'path_to_directory/client_secret.json',
    scopes=['https://www.googleapis.com/auth/calendar'])

flow.redirect_uri = 'https://www.example.com/oauth2callback'
```

## Motivation

Traditionally providers of OAuth endpoints have relied upon cut-and-paste as the way users of their service move the client id and secret from a registration page into working code. That can be error prone, along with it being an incomplete picture of all the information that is needed to get OAuth 2.0 working, which requires knowing all the endpoints and configuring a Redirect Endpoint. If service providers start providing a downloadable client_secrets.json file for client information and client libraries start consuming client_secrets.json then a large amount of friction in implementing OAuth 2.0 can be reduced.

