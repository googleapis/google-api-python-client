import os
import shutil
import sys
import importlib.util
import nox


BLACK_PATHS = [
    "googleapiclient",
    "apiclient",
    "tests",
    "noxfile.py",
    "setup.py",
    "describe.py",
    "samples-index.py",
    "sitecustomize.py",
]


@nox.session(python=["2.7", "3.4", "3.5", "3.6", "3.7"])
@nox.parametrize(
    "oauth2client",
    [
        "oauth2client<2dev",
        "oauth2client>=2,<=3dev",
        "oauth2client>=3,<=4dev",
        "oauth2client>=4,<=5dev",
    ],
)
def test(session, oauth2client):
    if session.python > "3":
        django = "django>=2.0.0"
    else:
        django = "django<2.0.0"
    session.install(oauth2client, "mox", "pyopenssl", "pycrypto==2.6", django)
    session.install("webtest", "nose", "coverage>=3.6,<3.99", "unittest2", "mock")
    session.install("e", ".")
    session.run(
        "nosetests",
        "--with-coverage",
        "--cover-package=googleapiclient",
        "--nocapture",
        "--cover-erase",
        "--cover-tests",
        "--cover-branches",
        "--cover-min-percentage=85",
    )


@nox.session(python="3.6")
def lint(session):
    session.install("flake8", "black")
    session.run("black", "--check", *BLACK_PATHS)
    session.run(
        "flake8",
        *BLACK_PATHS,
        "--count",
        "--select=E9,F63,F7,F82",
        "--show-source",
        "--statistics",
    )


@nox.session(python="3.6")
def blacken(session):
    session.install("black")
    session.run("black", *BLACK_PATHS)


@nox.session(python="3.7")
def docs(session):
    """Build the docs for this library."""

    session.install("-e", ".")
    session.install("sphinx", "alabaster", "recommonmark")

    shutil.rmtree(os.path.join("docs", "_build"), ignore_errors=True)
    session.run(
        "sphinx-build",
        "-W",  # warnings as errors
        "-T",  # show full traceback on exception
        "-N",  # no colors
        "-b",
        "html",
        "-d",
        os.path.join("docs", "_build", "doctrees", ""),
        os.path.join("docs", ""),
        os.path.join("docs", "_build", "html", ""),
    )