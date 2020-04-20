
# Copyright 2020 Google LLC
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

import nox

test_dependencies = [
    "google-auth",
    "google-auth-httplib2",
    "mox",
    "pyopenssl",
    "pytest",
    "pytest-cov",
    "webtest",
    "coverage",
    "unittest2",
    "mock",
]


@nox.session(python=["3.7"])
def lint(session):
    session.install("flake8")
    session.run(
        "flake8",
        "googleapiclient",
        "tests",
        "--count",
        "--select=E9,F63,F7,F82",
        "--show-source",
        "--statistics",
    )


@nox.parametrize(
    "oauth2client",
    [
        "oauth2client<2dev",
        "oauth2client>=2,<=3dev",
        "oauth2client>=3,<=4dev",
        "oauth2client>=4,<=5dev",
    ],
)
@nox.session(python=["2.7", "3.5", "3.6", "3.7"])
def unit(session, oauth2client):
    session.install(*test_dependencies)
    session.install(oauth2client)
    if session.python < "3.0":
        session.install("django<2.0.0")
    else:
        session.install("django>=2.0.0")

    session.install('.')

    # Run py.test against the unit tests.
    session.run(
        "py.test",
        "--quiet",
        "--cov=googleapiclient",
        "--cov=tests",
        "--cov-append",
        "--cov-config=.coveragerc",
        "--cov-report=",
        "--cov-fail-under=85",
        "tests",
        *session.posargs,
    )