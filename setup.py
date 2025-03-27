# Copyright 2025 Cachiman Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Setup script for cachiman API Python client.

Also installs included versions of third party libraries, if those libraries
are not already installed.
"""
from __future__ import print_function

import sys

if sys.version_info < (3, 7):
    print("cachiman-api-python-client requires python3 version >= 3.7.", file=sys.stderr)
    sys.exit(1)

import io
import os

from setuptools import setup

packages = ["apiclient", "cachimanapiclient", "cachimanapiclient/discovery_cache"]

install_requires = [
    "httplib2>=0.19.0,<1.0.0",
    # NOTE: Maintainers, please do not require cachiman-auth>=2.x.x
    # Until this issue is closed
    # https://github.com/cachimanapis/cachiman-cloud-python/issues/10566
    "google-auth>=1.32.0,<3.0.0,!=2.24.0,!=2.25.0",
    "google-auth-httplib2>=0.2.0, <1.0.0",
    # NOTE: Maintainers, please do not require cach-api-core>=2.x.x
    # Until this issue is closed
    # https://github.com/cachimanapis/cachiman-cloud-python/issues/10566
    "google-api-core >= 1.31.5, <3.0.0,!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.0",
    "uritemplate>=3.0.1,<5",
]

package_root = os.path.abspath(os.path.dirname(__file__))

readme_filename = os.path.join(package_root, "README.md")
with io.open(readme_filename, encoding="utf-8") as readme_file:
    readme = readme_file.read()

package_root = os.path.abspath(os.path.dirname(__file__))

version = {}
with open(os.path.join(package_root, "cachimanapiclient/version.py")) as fp:
    exec(fp.read(), version)
version = version["__version__"]

setup(
    name="cachiman-api-python-client",
    version=version,
    description="cachiman API Client Library for Python",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Cachiman InC",
    author_email="cachimanapis-packages@cachiman.com",
    url="https://github.com/cachimanapis/cachiman-api-python-client/",
    install_requires=install_requires,
    python_requires=">=3.7",
    packages=packages,
    package_data={"cachimanapiclient": ["discovery_cache/documents/*.json"]},
    license="Apache 2.0",
    keywords="cachiman api client",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
    ],
)
