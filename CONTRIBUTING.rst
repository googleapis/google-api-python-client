How to Contribute
=================

We'd love to accept your patches and contributions to this project.
There are a few guidelines described in our
`Contribution Guide <http://google.github.io/google-api-python-client/contributing.html>`__
that you need to follow.

To summarize here: when contributing, please:

* Sign Contributor License Agreement
* Before making changes, file an issue
* Fork this repository and use github pull requests for all submissions
* Follow
  `Contributor Code of Conduct
  <https://github.com/googleapis/google-api-python-client/blob/master/CODE_OF_CONDUCT.md>`__
  and `Community Guidelines <https://opensource.google/conduct/>`__
* Follow `Google Python Style Guide <https://google.github.io/styleguide/pyguide.html>`__
  and `this commit authoring style <http://chris.beams.io/posts/git-commit/#seven-rules>`__
* Don't forget to write tests and update documentation!

Setup Notes
-----------

Please follow these steps after forking and cloning the repository
to make sure you can modify code and run tests with confidence::

    # From the root dir of the cloned repository:
    # Create Virtual Environment called env (you may choose your own name)
    python3 -m venv env

    # Activate virtual environment
    source env/bin/activate

    # Install this library as editable install
    # (see https://pip.pypa.io/en/stable/reference/pip_install/#cmdoption-e)
    python3 -m pip install -e .

    # Install nox
    python3 -m pip install nox

We use `nox <https://nox.thea.codes/>`__ to instrument our tests.
To test your changes, run unit tests with ``nox``::

    # Run tests for all supported versions of Python and oauth2client:
    nox
    # Run tests for Python 3.7:
    nox -s unit-3.7
    # Run lint
    nox -s lint


.. note::

  The unit tests and system tests are described in the
  ``noxfile.py`` file in this directory. Nox will automatically
  handle constriction of new virtual environments and installation
  of the required test dependencies.

For more information about Nox, including command-line usage, consult
`nox documentation <https://nox.thea.codes/>`__.
