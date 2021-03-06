.. highlight:: shell

============
Installation
============


Stable release
--------------

To install parselglossy, run this command in your terminal:

.. code-block:: console

    $ pip install parselglossy

This is the preferred method to install parselglossy, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for parselglossy can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/dev-cafe/parselglossy

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/dev-cafe/parselglossy/tarball/master

Once you have a copy of the source, you can install it using `Flit <https://flit.readthedocs.io/en/latest/index.html/>`_:

.. code-block:: console

    $ virtualenv venv
    $ pip install --upgrade flit
    $ flit install --symlink 


.. _Github repo: https://github.com/dev-cafe/parselglossy
.. _tarball: https://github.com/dev-cafe/parselglossy/tarball/master
