# Using OAuth 2.0 for Server to Server Applications

The Google APIs Client Library for Python supports using OAuth 2.0 for server-to-server interactions such as those between a web application and a Google service. For this scenario you need a service account, which is an account that belongs to your application instead of to an individual end user. Your application calls Google APIs on behalf of the service account, so users aren't directly involved. This scenario is sometimes called "two-legged OAuth," or "2LO." (The related term "three-legged OAuth" refers to scenarios in which your application calls Google APIs on behalf of end users, and in which user consent is sometimes required.)

Typically, an application uses a service account when the application uses Google APIs to work with its own data rather than a user's data. For example, an application that uses [Google Cloud Datastore](https://cloud.google.com/datastore/) for data persistence would use a service account to authenticate its calls to the Google Cloud Datastore API.

If you have a G Suite domain—if you use [G Suite](https://gsuite.google.com/), for example—an administrator of the G Suite domain can authorize an application to access user data on behalf of users in the G Suite domain. For example, an application that uses the [Google Calendar API](Google Calendar API) to add events to the calendars of all users in a G Suite domain would use a service account to access the Google Calendar API on behalf of users. Authorizing a service account to access data on behalf of users in a domain is sometimes referred to as "delegating domain-wide authority" to a service account.

> **Note:** When you use [G Suite Marketplace](https://www.google.com/enterprise/marketplace/) to install an application for your domain, the required permissions are automatically granted to the application. You do not need to manually authorize the service accounts that the application uses.

> **Note:** Although you can use service accounts in applications that run from a Google Apps domain, service accounts are not members of your Google Apps account and aren't subject to domain policies set by Google Apps administrators. For example, a policy set in the Google Apps admin console to restrict the ability of Apps end users to share documents outside of the domain would not apply to service accounts.

This document describes how an application can complete the server-to-server OAuth 2.0 flow by using the Google APIs Client Library for Python.

## Overview

To support server-to-server interactions, first create a service account for your project in the API Console. If you want to access user data for users in your Google Apps domain, then delegate domain-wide access to the service account.

Then, your application prepares to make authorized API calls by using the service account's credentials to request an access token from the OAuth 2.0 auth server.

Finally, your application can use the access token to call Google APIs.

## Creating a service account

A service account's credentials include a generated email address that is unique, a client ID, and at least one public/private key pair.

If your application runs on Google App Engine, a service account is set up automatically when you create your project.

If your application runs on Google Compute Engine, a service account is also set up automatically when you create your project, but you must specify the scopes that your application needs access to when you create a Google Compute Engine instance. For more information, see [Preparing an instance to use service accounts](https://cloud.google.com/compute/docs/authentication#using).

If your application doesn't run on Google App Engine or Google Compute Engine, you must obtain these credentials in the Google API Console. To generate service-account credentials, or to view the public credentials that you've already generated, do the following:

1. Open the [**Service accounts** page](https://console.developers.google.com/permissions/serviceaccounts). If prompted, select a project.
1. Click **Create service account**.
1. In the **Create service account** window, type a name for the service account, and select **Furnish a new private key**. If you want to [grant G Suite domain-wide authority](https://developers.google.com/identity/protocols/OAuth2ServiceAccount#delegatingauthority) to the service account, also select **Enable G Suite Domain-wide Delegation**. Then click **Create**.

Your new public/private key pair is generated and downloaded to your machine; it serves as the only copy of this key. You are responsible for storing it securely.

You can return to the [API Console](https://console.developers.google.com/) at any time to view the client ID, email address, and public key fingerprints, or to generate additional public/private key pairs. For more details about service account credentials in the API Console, see [Service accounts](https://developers.google.com/console/help/service-accounts) in the API Console help file.

Take note of the service account's email address and store the service account's private key file in a location accessible to your application. Your application needs them to make authorized API calls.

> **Note:** You must store and manage private keys securely in both development and production environments. Google does not keep a copy of your private keys, only your public keys.

## Delegating domain-wide authority to the service account

If your application runs in a Google Apps domain and accesses user data, the service account that you created needs to be granted access to the user data that you want to access.

The following steps must be performed by an administrator of the Google Apps domain:

1. Go to your Google Apps domain’s [Admin console](http://admin.google.com/).
1. Select **Security** from the list of controls. If you don't see **Security** listed, select **More controls** from the gray bar at the bottom of the page, then select **Security** from the list of controls. If you can't see the controls, make sure you're signed in as an administrator for the domain.
1. Select **Advanced settings** from the list of options.
1. Select **Manage third party OAuth Client access** in the **Authentication** section.
1. In the **Client name** field enter the service account's **Client ID**.
1. In the **One or More API Scopes** field enter the list of scopes that your application should be granted access to. For example, if your application needs domain-wide access to the Google Drive API and the Google Calendar API, enter: `https://www.googleapis.com/auth/drive`, `https://www.googleapis.com/auth/calendar`.
1. Click **Authorize**.

Your application now has the authority to make API calls as users in your domain (to "impersonate" users). When you prepare to make authorized API calls, you specify the user to impersonate.

## Preparing to make an authorized API call

After you obtain the client email address and private key from the API Console, complete the following steps:

1. Install the required libraries:

    ```sh
    pip install google-auth google-auth-httplib2 google-api-python-client
    ```

1. Create a `Credentials` object from the service account's credentials and the scopes your application needs access to. For example:

### Examples

#### Google App Engine standard environment	

```py
from google.auth import app_engine

SCOPES = ['https://www.googleapis.com/auth/sqlservice.admin']

credentials = app_engine.Credentials(scopes=SCOPES)
```

> **Note:** You can only use App Engine credential objects in applications that are running in a Google App Engine standard environment. If you need to run your application in other environments—for example, to test your application locally—you must detect this situation and use a different credential mechanism (see [Other platforms](https://developers.google.com/api-client-library/python/auth/service-accounts#jwtsample)).

#### Google Compute Engine

```py
from google.auth import compute_engine

credentials = compute_engine.Credentials()
```

You must [configure your Compute Engine instance to allow access to the necessary scopes](https://cloud.google.com/compute/docs/access/create-enable-service-accounts-for-instances#changeserviceaccountandscopes).

> **Note:** You can only use Compute Engine credential objects in applications that are running on Google Compute Engine. If you need to run your application in other environments—for example, to test your application locally—you must detect this situation and use a different credential mechanism (see [Other platforms](https://developers.google.com/api-client-library/python/auth/service-accounts#jwtsample)). You can use the [application default credentials](https://developers.google.com/accounts/docs/application-default-credentials) to simplify this process.

#### Other Platforms

```py
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/sqlservice.admin']
SERVICE_ACCOUNT_FILE = '/path/to/service.json'

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
```

Use the `Credentials` object to call Google APIs in your application.

## Calling Google APIs

To call a Google API using the `Credentials` object, complete the following steps:

1. Build a service object for the API that you want to call. You build a a service object by calling the build function with the name and version of the API and the authorized Http object. For example, to call version 1beta3 of the [Cloud SQL Administration API](https://cloud.google.com/sql/docs/admin-api/):

    ```py
    import googleapiclient.discovery

    sqladmin = googleapiclient.discovery.build('sqladmin', 'v1beta3', credentials=credentials)
    ```

1. Make requests to the API service using the [interface provided by the service object](https://developers.google.com/api-client-library/python/start/get_started#build). For example, to list the instances of Cloud SQL databases in the example-123 project:

    ```py
    response = sqladmin.instances().list(project='example-123').execute()
    ```

## Complete example

The following example prints a JSON-formatted list of Cloud SQL instances in a project.

```py
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