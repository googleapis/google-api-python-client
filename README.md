# Google API Client

[![PyPI version](https://badge.fury.io/py/google-api-python-client.svg)](https://badge.fury.io/py/google-api-python-client)

This is the Python client library for Google's discovery based APIs. To get started, please see the [docs folder](docs/README.md).

These client libraries are officially supported by Google.  However, the libraries are considered complete and are in maintenance mode. This means that we will address critical bugs and security issues but will not add any new features.

## Documentation

See the [docs folder](docs/README.md) for more detailed instructions and additional documentation.

## Other Google API libraries

For Google Cloud Platform APIs such as Datastore, Cloud Storage or Pub/Sub, we recommend using [Cloud Client Libraries for Python](https://github.com/GoogleCloudPlatform/google-cloud-python).

For Google Ads API, we recommend using [Google Ads API Client Library for Python](https://github.com/googleads/google-ads-python/).

For Google Firebase Admin API, we recommend using [Firebase Admin Python SDK](https://github.com/firebase/firebase-admin-python).

## Installation

Install this library in a [virtualenv](https://virtualenv.pypa.io/en/latest/) using pip. virtualenv is a tool to
create isolated Python environments. The basic problem it addresses is one of
dependencies and versions, and indirectly permissions.

With virtualenv, it's possible to install this library without needing system
install permissions, and without clashing with the installed system
dependencies.

### Mac/Linux

```
pip install virtualenv
virtualenv <your-env>
source <your-env>/bin/activate
<your-env>/bin/pip install google-api-python-client
```

### Windows

```
pip install virtualenv
virtualenv <your-env>
<your-env>\Scripts\activate
<your-env>\Scripts\pip.exe install google-api-python-client
```

## Supported Python Versions

Python 3.4, 3.5, 3.6 and 3.7 are fully supported and tested. This library may work on later versions of 3, but we do not currently run tests against those versions

## Deprecated Python Versions

Python == 2.7

## Third Party Libraries and Dependencies

The following libraries will be installed when you install the client library:
* [httplib2](https://github.com/httplib2/httplib2)
* [uritemplate](https://github.com/sigmavirus24/uritemplate)

For development you will also need the following libraries:
* [WebTest](http://webtest.pythonpaste.org/en/latest/index.html)
* [pyopenssl](https://pypi.python.org/pypi/pyOpenSSL)

## Contributing

Please see the [contributing page](http://google.github.io/google-api-python-client/contributing.html) for more information. In particular, we love pull requests - but please make sure to sign the contributor license agreement.
