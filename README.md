# Google API Client

[![PyPI version](https://badge.fury.io/py/google-api-python-client.svg)](https://badge.fury.io/py/google-api-python-client)
[![Compat check PyPI](https://python-compatibility-tools.appspot.com/one_badge_image?package=google-api-python-client)](https://python-compatibility-tools.appspot.com/one_badge_target?package=google-api-python-client)
[![Compat check github](https://python-compatibility-tools.appspot.com/one_badge_image?package=git%2Bgit%3A//github.com/googleapis/google-api-python-client.git)](https://python-compatibility-tools.appspot.com/one_badge_target?package=git%2Bgit%3A//github.com/googleapis/google-api-python-client.git)

This is the Python client library for Google's discovery based APIs. To get started, please see the [full documentation for this library](https://developers.google.com/api-client-library/python/). Additionally, [dynamically generated documentation](http://google.github.io/google-api-python-client/docs/epy/index.html) is available for all of the APIs supported by this library.

These client libraries are officially supported by Google.  However, the libraries are considered complete and are in maintenance mode. This means that we will address critical bugs and security issues but will not add any new features.

## Documentation

See the [docs folder](docs/README.md) for more detailed instructions and additional documentation.

## Google Cloud Platform

For Google Cloud Platform APIs such as Datastore, Cloud Storage or Pub/Sub, we recommend using [Cloud Client Libraries for Python](https://github.com/GoogleCloudPlatform/google-cloud-python) which is under active development.

## Installation

To install, simply use `pip` or `easy_install`:

```bash
pip install --upgrade google-api-python-client
```

or

```bash
easy_install --upgrade google-api-python-client
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
* [pycrypto](https://pypi.python.org/pypi/pycrypto)
* [pyopenssl](https://pypi.python.org/pypi/pyOpenSSL)

## Contributing

Please see the [contributing page](http://google.github.io/google-api-python-client/contributing.html) for more information. In particular, we love pull requests - but please make sure to sign the contributor license agreement.
