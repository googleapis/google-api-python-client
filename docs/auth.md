# Authentication Overview

This document is an overview of how authentication, authorization, and accounting are accomplished. For all API calls, your application needs to be authenticated. When an API accesses a user's private data, your application must also be authorized by the user to access the data. For example, accessing a public Google+ post would not require user authorization, but accessing a user's private calendar would. Also, for quota and billing purposes, all API calls involve accounting. This document summarizes the protocols used by Google APIs and provides links to more information.

## Access types

It is important to understand the basics of how API authentication and authorization are handled. All API calls must use either simple or authorized access (defined below). Many API methods require authorized access, but some can use either. Some API methods that can use either behave differently, depending on whether you use simple or authorized access. See the API's method documentation to determine the appropriate access type.

### 1. Simple API access (API keys)

These API calls do not access any private user data. Your application must authenticate itself as an application belonging to your Google API Console project. This is needed to measure project usage for accounting purposes.

**API key:** To authenticate your application, use an [API key](api-keys.md) for your API Console project. Every simple access call your application makes must include this key.

> **Warning:** Keep your API key private. If someone obtains your key, they could use it to consume your quota or incur charges against your API Console project.

### 2. Authorized API access (OAuth 2.0)

These API calls access private user data. Before you can call them, the user that has access to the private data must grant your application access. Therefore, your application must be authenticated, the user must grant access for your application, and the user must be authenticated in order to grant that access. All of this is accomplished with OAuth 2.0 and libraries written for it.

**Scope:** Each API defines one or more scopes that declare a set of operations permitted. For example, an API might have read-only and read-write scopes. When your application requests access to user data, the request must include one or more scopes. The user needs to approve the scope of access your application is requesting.

**Refresh and access tokens:** When a user grants your application access, the OAuth 2.0 authorization server provides your application with refresh and access tokens. These tokens are only valid for the scope requested. Your application uses access tokens to authorize API calls. Access tokens expire, but refresh tokens do not. Your application can use a refresh token to acquire a new access token.

> **Warning:** Keep refresh and access tokens private. If someone obtains your tokens, they could use them to access private user data.

**Client ID and client secret:** These strings uniquely identify your application and are used to acquire tokens. They are created for your project on the [API Console](https://console.developers.google.com/). There are three types of client IDs, so be sure to get the correct type for your application:

- [Web application](https://developers.google.com/accounts/docs/OAuth2WebServer) client IDs
- [Installed application](https://developers.google.com/accounts/docs/OAuth2InstalledApp) client IDs
- [Service Account](https://developers.google.com/accounts/docs/OAuth2ServiceAccount) client IDs

> **Warning:** Keep your client secret private. If someone obtains your client secret, they could use it to consume your quota, incur charges against your Console project, and request access to user data.

## Using API keys

More information and examples for API keys are provided on the [API Keys](api-keys.md) page.

## Using OAuth 2.0

More information and examples for OAuth 2.0 are provided on the [OAuth 2.0](oauth.md) page.
