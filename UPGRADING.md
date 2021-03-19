# 2.0.0 Migration Guide

The 2.0 release of `google-api-python-client` is a significant upgrade as only
python 3.6 and newer is supported. If you are not able to upgrade python, then
please continue to use version 1.x as we will continue supporting python 2.7+ in
[v1](https://github.com/googleapis/google-api-python-client/tree/v1).

In addition, discovery documents will no longer be retrieved dynamically when
you call  `discovery.build()`. The discovery documents will instead be retrieved
from the client library directly. As a result of caching the discovery
documents, the size of this package is at least 50 MB larger compared to the
previous version.


For users of public APIs
------------------------
Existing code written for earlier versions of this library will not require
updating. We believe this new default behaviour will provide a more predictable
experience for users. If always using the latest version of a service definition
is more important than reliability, users should set the `static_discovery`
argument of `discovery.build()` to `False` to retrieve the service definition
from the internet.

For users of private APIs
-------------------------
If the discovery document requires an authentication key to access it, the
discovery document is private and it will not be shipped with the library.
Only discovery documents listed in [this public directory](https://www.googleapis.com/discovery/v1/apis/)
are included in the library. Users of private APIs should set the
`static_discovery` argument of `discovery.build()` to `False` to continue to
retrieve the service definition from the internet. As of version 2.1.0,
for backwards compatability with version 1.x, if `static_discovery` is not
specified, the default value for `static_discovery` will be `True` when
the `discoveryServiceUrl` argument of `discovery.build()` is provided.

If you experience issues or have questions, please file an [issue](https://github.com/googleapis/google-api-python-client/issues).

## Supported Python Versions

> **WARNING**: Breaking change

The 2.0.0 release requires Python 3.6+, as such you must upgrade to Python 3.6+
to use version 2.0.0.

## Method Calls

**Note**: Existing code written for earlier versions of this library will not
require updating. You should only update your code if always using the latest
version of a service definition is more important than reliability or if you
are using an API which does not have a public discovery document.

> **WARNING**: Breaking change

The 2.0.0 release no longer retrieves discovery documents dynamically on each
call to `discovery.build()`. Instead, discovery documents are retrieved from
the client library itself.

Under the hood, the `discovery.build()` function retrieves a discovery artifact
in order to construct the service object. The breaking change is that the
`discovery.build()` function will no longer retrieve discovery artifacts
dynamically. Instead it will use service definitions shipped in the library.


**Before:**
```py
from googleapiclient.discovery import build

# Retrieve discovery artifacts from the internet
with build('drive', 'v3') as service:
    # ...
```

**After:**
```py
from googleapiclient.discovery import build

# Retrieve discovery artifacts from the client library
with build('drive', 'v3') as service:
    # ...

# Retrieve discovery artifacts from the internet
with build('drive', 'v3', static_discovery=False) as service:
    # ...
```
