.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/dev-cafe/parselglossy/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

parselglossy could always use more documentation, whether as part of the
official parselglossy docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/dev-cafe/parselglossy/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `parselglossy` for local development.

1. Fork the `parselglossy` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/parselglossy.git

3. Install your local copy into a virtual environment. We recommend using `Pipenv <https://pipenv.readthedocs.io/en/latest/>`_.
   This is how you set up your fork for local development::

    $ pipenv install --dev -e .

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the
   tests::

    $ flake8 parselglossy tests
    $ py.test

   To get flake8, just pip install it into your virtual environment.

5. Formatting of your contributions should be coherent with that of the rest of
   the code. We use Black_ and its default code style. Black_ is beta software
   and requires Python 3.6+, but it can easily be installed in your virtual
   environment.
   The code ships with Git pre-commit hooks. You can install `pre-commit <https://github.com/pre-commit/pre-commit>`_ and enable them with::

    $ pre-commit install --install-hooks

7. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -sm "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

   Note the use of the ``-s`` flag when committing. This ensures that you have
   read and agreed to the **Developer Certificate of Origin** (DCO_) by *signing
   off* your commits.

8. Submit a pull request through the GitHub website.

.. _Black: https://black.readthedocs.io/en/stable/
.. _DCO: https://developercertificate.org/

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. All commits should be signed-off
2. The pull request should include tests.
3. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in ``README.rst``.
4. The pull request should work for Python 3.6 and 3.7. Check
   https://travis-ci.org/dev-cafe/parselglossy/pull_requests
   and make sure that the tests pass for all supported Python versions.

Additional Development Packages
---------------------------------

There are many ways you can set up your development environment to work on ``parselglossy``.
The minimal, working specification is given in the ``Pipfile`` and will allow you to run test as done on the continuous integration services.
In addition to the essential development packages, you might want to additionally install:

* `Python language server <https://github.com/palantir/python-language-server>`_
  for modern integration with your editor. Note that this will need some
  configuration work on your part to set up the integration.
* `mypy <http://mypy-lang.org/>`_ for optional type checking and the
  ``pyls-mypy`` integration plugin with the language server. As the library
  evolves and stabilises, we might introduce type checking as an additional test
  to the test suite.
* `isort <https://isort.readthedocs.io/en/latest/>`_ for automatic sorting of
  ``import`` statements and the ``pyls-isort`` integration plugin with language
  server.
* The ``pyls-black`` integration plugin for the Black code formatter and the language server.
* If you use Emacs, `importmagic <https://github.com/alecthomas/importmagic>`_
  can be integrated to provide symbol resolution.

Deploying
---------

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in ``HISTORY.rst``).
Then run:

1. Bump the version by editing ``__version__`` in ``parselglossy/__init__.py``.
   For this follow `PEP 440 <https://www.python.org/dev/peps/pep-0440/>`_.

2. Stage and commit the change to a branch::

   $ git add parselglossy/__init__.py
   $ git commit -sm "Bump version: x.y.z -> X.Y.Z"

3. Submit a pull request targeting either the ``master`` branch or a
   release branch.

4. Once the pull request is accepted, create and push a tag. Travis will then automatically deploy to PyPI if tests pass for the Python 3.6 lane::

   $ git tag -a vX.Y.Z -m "Version X.Y.Z release" -s # -s is to GPG-sign the tag

5. If everything worked out, write a minimal summary of the release *via* the
   GitHub web user interface.
