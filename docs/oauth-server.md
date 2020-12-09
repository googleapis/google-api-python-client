# Using OAuth 2.0 for Server to Server Applications

The Google APIs Client Library for Python supports using OAuth 2.0 for server-to-server interactions such as those between a web application and a Google service. For this scenario you need a service account, which is an account that belongs to your application instead of to an individual end user. Your application calls Google APIs on behalf of the service account, so users aren't directly involved. This scenario is sometimes called "two-legged OAuth," or "2LO." (The related term "three-legged OAuth" refers to scenarios in which your application calls Google APIs on behalf of end users, and in which user consent is sometimes required.)

Typically, an application uses a service account when the application uses Google APIs to work with its own data rather than a user's data. For example, an application that uses [Google Cloud Datastore](https://cloud.google.com/datastore/) for data persistence would use a service account to authenticate its calls to the Google Cloud Datastore API.

If you have a G Suite domain—if you use [G Suite](https://gsuite.google.com/), for example—an administrator of the G Suite domain can authorize an application to access user data on behalf of users in the G Suite domain. For example, an application that uses the [Google Calendar API](https://developers.google.com/calendar/) to add events to the calendars of all users in a G Suite domain would use a service account to access the Google Calendar API on behalf of users. Authorizing a service account to access data on behalf of users in a domain is sometimes referred to as "delegating domain-wide authority" to a service account.

> **Note:** When you use [G Suite Marketplace](https://www.google.com/enterprise/marketplace/) to install an application for your domain, the required permissions are automatically granted to the application. You do not need to manually authorize the service accounts that the application uses.

> **Note:** Although you can use service accounts in applications that run from a G Suite domain, service accounts are not members of your G Suite account and aren't subject to domain policies set by G Suite administrators. For example, a policy set in the G Suite Admin console to restrict the ability of G Suite end users to share documents outside of the domain would not apply to service accounts. Similarly, that policy would prevent users from sharing documents with service accounts, because service acounts are always outside of the domain. If you're using G Suite domain-wide delegation, this isn't relevant to you - you are accessing APIs while acting as a domain user, not as the service account itself.

This document describes how an application can complete the server-to-server OAuth 2.0 flow by using the Google APIs Client Library for Python.

## Overview

To support server-to-server interactions, first create a service account for your project in the API Console. If you want to access user data for users in your G Suite domain, then delegate domain-wide access to the service account.

Then, your application prepares to make authorized API calls by using the service account's credentials to request an access token from the OAuth 2.0 auth server.

Finally, your application can use the access token to call Google APIs.

## Creating a service account

https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys


## Delegating domain-wide authority to the service account

If your application runs in a G Suite domain and accesses user data, the service account that you created needs to be granted access to the user data that you want to access.

https://developers.google.com/admin-sdk/directory/v1/guides/delegation

## Preparing to make an authorized API call

After you obtain the client email address and private key from the API Console, complete the following steps:

1. Install the required libraries:

    ```sh
    pip install google-auth google-auth-httplib2 google-api-python-client
    ```

1. Create a `Credentials` object from the service account's credentials and the scopes your application needs access to. For example:

### Examples

#### Application Default Credentials

Application Default Credentials abstracts authentication across the different Google Cloud Platform hosting environments. When running on any Google Cloud hosting environment or when running locally with the Google Cloud SDK installed, `google.auth.default()` can automatically determine the credentials from the environment. See https://google.aip.dev/auth/4110 and https://googleapis.dev/python/google-auth/latest/user-guide.html#application-default-credentials for details.

```python
import google.auth

SCOPES = ['https://www.googleapis.com/auth/sqlservice.admin']

credentials, project = google.auth.default(scopes=SCOPES)
```

#### Other Platforms
Obtain a service account key file  by following this guide: 
https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys
```python
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/sqlservice.admin']
SERVICE_ACCOUNT_FILE = '/path/to/service.json'

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
```

Use the `credentials` object to call Google APIs in your application.

#### Using Domain-wide Delegation

```python
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/sqlservice.admin']
SERVICE_ACCOUNT_FILE = '/path/to/service.json'

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES, subject='user@domain.com')
```

Use the `credentials` object to call Google APIs in your application. The API requests would be authorized as `user@domain.com`, if you've authorized the service account accordingly in the G Suite Admin console.


## Calling Google APIs

To call a Google API using the `Credentials` object, complete the following steps:

1. Build a service object for the API that you want to call. You build a a service object by calling the build function with the name and version of the API and the authorized Http object. For example, to call version 1beta3 of the [Cloud SQL Administration API](https://cloud.google.com/sql/docs/admin-api/):

    ```python
    import googleapiclient.discovery

    sqladmin = googleapiclient.discovery.build('sqladmin', 'v1beta3', credentials=credentials)
    ```

1. Make requests to the API service using the interface provided by the service object. For example, to list the instances of Cloud SQL databases in the example-123 project:

    ```python
    response = sqladmin.instances().list(project='example-123').execute()
    ```

## Complete example

The following example prints a JSON-formatted list of Cloud SQL instances in a project.

```python
from google.oauth2 import service_account
import googleapiclient.discovery

SCOPES = ['https://www.googleapis.com/auth/sqlservice.admin']
SERVICE_ACCOUNT_FILE = '/path/to/service.json'

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
sqladmin = googleapiclient.discovery.build('sqladmin', 'v1beta3', credentials=credentials)
response = sqladmin.instances().list(project='exemplary-example-123').execute()

print(response)
```
