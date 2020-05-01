# Using OAuth 2.0 for Web Server Applications

This document explains how web server applications use the Google API Client Library for Python to implement OAuth 2.0 authorization to access Google APIs. OAuth 2.0 allows users to share specific data with an application while keeping their usernames, passwords, and other information private. For example, an application can use OAuth 2.0 to obtain permission from users to store files in their Google Drives.

This OAuth 2.0 flow is specifically for user authorization. It is designed for applications that can store confidential information and maintain state. A properly authorized web server application can access an API while the user interacts with the application or after the user has left the application.

Web server applications frequently also use [service accounts](service-accounts.md) to authorize API requests, particularly when calling Cloud APIs to access project-based data rather than user-specific data. Web server applications can use service accounts in conjunction with user authorization.

## Prerequisites

### Enable APIs for your project

Any application that calls Google APIs needs to enable those APIs in the API Console. To enable the appropriate APIs for your project:

1. Open the [Library](https://console.developers.google.com/apis/library) page in the API Console.
1. Select the project associated with your application. Create a project if you do not have one already.
1. Use the **Library** page to find each API that your application will use. Click on each API and enable it for your project.

### Create authorization credentials

Any application that uses OAuth 2.0 to access Google APIs must have authorization credentials that identify the application to Google's OAuth 2.0 server. The following steps explain how to create credentials for your project. Your applications can then use the credentials to access APIs that you have enabled for that project.

<ol>
  <li>Open the <a href="https://console.developers.google.com/apis/credentials">Credentials page</a> in the API Console.</li>

  <li>Click <b>Create credentials &gt; OAuth client ID</b>.</li>
  <li>Complete the form. Set the application type to <code>Web
      application</code>. Applications that use languages and frameworks
      like PHP, Java, Python, Ruby, and .NET must specify authorized
      <b>redirect URIs</b>. The redirect URIs are the endpoints to which the
      OAuth 2.0 server can send responses.<br><br>
      For testing, you can specify URIs that refer to the local machine,
      such as <code>http://localhost:8080</code>. With that in mind, please
      note that all of the examples in this document use
      <code>http://localhost:8080</code> as the redirect URI.
      <br><br>
      We recommend that you <a href="#protectauthcode">design your app's auth
      endpoints</a> so that your application does not expose authorization
      codes to other resources on the page.</li>
</ol>

After creating your credentials, download the **client_secret.json** file from the API Console. Securely store the file in a location that only your application can access.

> **Important:** Do not store the **client_secret.json** file in a publicly-accessible location. In addition, if you share the source code to your application—for example, on GitHub—store the **client_secret.json** file outside of your source tree to avoid inadvertently sharing your client credentials.

### Identify access scopes

Scopes enable your application to only request access to the resources that it needs while also enabling users to control the amount of access that they grant to your application. Thus, there may be an inverse relationship between the number of scopes requested and the likelihood of obtaining user consent.

Before you start implementing OAuth 2.0 authorization, we recommend that you identify the scopes that your app will need permission to access.

We also recommend that your application request access to authorization scopes via an incremental authorization process, in which your application requests access to user data in context. This best practice helps users to more easily understand why your application needs the access it is requesting.

The [OAuth 2.0 API Scopes document](https://developers.google.com/identity/protocols/googlescopes) contains a full list of scopes that you might use to access Google APIs.