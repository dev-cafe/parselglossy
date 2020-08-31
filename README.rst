============
parselglossy
============


.. image:: https://img.shields.io/pypi/v/parselglossy.svg
        :target: https://pypi.python.org/pypi/parselglossy

.. image:: https://github.com/dev-cafe/parselglossy/workflows/Test%20parselglossy/badge.svg?branch=master
        :target: https://github.com/dev-cafe/parselglossy/actions?query=workflow%3A%22Test+parselglossy%22+branch%3Amaster
        :alt: CI build status
        
.. image:: https://codecov.io/gh/dev-cafe/parselglossy/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/dev-cafe/parselglossy

.. image:: https://readthedocs.org/projects/parselglossy/badge/?version=latest
        :target: https://parselglossy.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status



.. epigraph::

   [...] I speak with tongues more than you all;

   -- **1 Corinthians** 14:18

   Parse it on!

   -- Bobson Dugnutt, **Private communication**


Generic input parsing library, speaking in tongues.

``parselglossy`` generates a fully functional Python input parsing module from a
simple YAML template specification.  The parser has *no dependencies* on
external Python packages.
The documentation for all input keywords is also generated in reStructuredText
format from the YAML specification.


.. image:: https://github.com/dev-cafe/parselglossy/raw/master/docs/gfx/parse.jpg
     :alt: Parse all the inputs!

* Free software: MIT license
* Documentation: https://parselglossy.readthedocs.io.


Requirements
------------

* Python 3.6 or later.


Features
--------

* **Flexible**. It can accommodate different input styles and still generate
  correct parsers.  This is achieved by decoupling input reading and validation.
* **Extensible**. We work with standard Python types and standard JSON format.
  Interfacing and extending to your needs is straightforward.
* **Simple**. Just provide an input specification in YAML format: names of
  keywords/sections, defaults, documentation. The tedious bits are automatically
  handled for you.
* **Correct**. ``parselglossy`` gives two correctness guarantees:

  1. If the YAML specification is valid, the generated parser will be correct.
  2. If validation completes, the input to your application is well-formed.

Projects using parselglossy
---------------------------

*  `MRChem <https://mrchem.readthedocs.io/en/latest/>`_

If your project is using parselglossy, please add a link via a pull request.
