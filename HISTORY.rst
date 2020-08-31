=======
History
=======

0.7.0_ (2020-08-31)
-------------------

* The ``validate`` function in the API of the generated input parser now accepts
  a Python ``dict`` as intermediate representation.  This might be useful when
  wanting to validate input programmatically, *i.e.* avoiding writing
  intermediate files on disk.
* Prune ``docstring`` element from template during generation. This reduces the
  lines of code produced when creating the input parser module.

0.6.0_ (2020-08-25)
-------------------

* Redistribute template validation functions in ``check_template.py``. This
  avoids exposing internal dependencies in the generated parser.

0.5.0_ (2020-08-15)
-------------------

* ``parselglossy`` can now *reorder* noncyclic dependencies between keywords'
  defaulting actions at validation time.
  See PR `#99 <https://github.com/dev-cafe/parselglossy/pull/99>`_.
* ``parselglossy`` can now *detect* cyclic dependencies between keywords'
  defaulting actions at validation time.
  A validation specification like the following:

  .. code-block:: yaml

     - name: some_number
       type: int
       default: "user['another_number']"
       docstring: |
         Some number which defaults to the value of another_number.
     - name: another_number
       type: int
       default: "user['some_number']"
       docstring: |
         Another number which defaults to the value of some_number.

  will be flagged as invalid due to the cyclic dependency between keywords.
  See PR `#96 <https://github.com/dev-cafe/parselglossy/pull/96>`_.
* ``parselglossy`` can now *generate* an input parsing Python module which only
  depends on a standard Python distribution.
  See PR `#84 <https://github.com/dev-cafe/parselglossy/pull/84>`_.
* Switch to `Flit <https://flit.readthedocs.io/en/latest/index.html/>`_ to manage packaging.
  We recommend a good old virtualenv+pip for dependencies and virtual environment. See PRs
  `#87 <https://github.com/dev-cafe/parselglossy/pull/87>`_,
  `#88 <https://github.com/dev-cafe/parselglossy/pull/88>`_,
  `#93 <https://github.com/dev-cafe/parselglossy/pull/93>`_,
  `#95 <https://github.com/dev-cafe/parselglossy/pull/95>`_.
* **BREAKING** ``parselglossy`` provides only a minimal CLI for generating an input parser.
  The full-fledged parsing functionality is, for the moment, retained in the API.
  See PR `#97 <https://github.com/dev-cafe/parselglossy/pull/97>`_.
* Input parsers generated with ``parselglossy`` will now raise an exception when
  keywords have been repeated in an input file.
  See PR `#89 <https://github.com/dev-cafe/parselglossy/pull/89>`_.
* Dropped support for Python 3.5

0.3.0_ (2019-03-31)
-------------------

* Fix Travis automatic deployment to PyPI.
* Fix build of API docs on ReadTheDocs.

0.3.0-alpha2_ (2019-03-29)
--------------------------

* Update ``CONTRIBUTING.rst``.

0.3.0-alpha1_ (2019-03-28)
--------------------------

* Dropped support for Python 3.4.
* Renamed the ``section`` and ``keyword`` fields in the template to ``name``.
* Renamed the ``documentation`` field in the template to ``docstring``.
* Arbitrary callables of the input dictionary are now allowed in the ``default``
  field. Fix `#31 <https://github.com/dev-cafe/parselglossy/issues/31>`_.
* Complex numbers have the proper type after reading in. Fix `#26 <https://github.com/dev-cafe/parselglossy/issues/26>`_.
* Better error reporting. Exceptions are raised after each validation stage and
  offer detail error messages that give a comprehensive overview of what went
  wrong. Fix `#24 <https://github.com/dev-cafe/parselglossy/issues/24>`_.
* Fully defaulted sections are now properly taken into account. Fix `#33
  <https://github.com/dev-cafe/parselglossy/issues/33>`_.
* Nesting of sections under keywords will throw an exception. Fix `#34
  <https://github.com/dev-cafe/parselglossy/issues/34>`_.

0.2.0_ (2019-03-11)
-------------------

* Implementation of the Getkw_ input grammar.
* Implementation of the validation infrastructure.

0.1.0_ (2018-12-03)
-------------------

* First release on PyPI.


.. _Unreleased: https://github.com/dev-cafe/parselglossy/compare/v0.7.0...HEAD
.. _0.7.0: https://github.com/dev-cafe/parselglossy/releases/tag/v0.7.0
.. _0.6.0: https://github.com/dev-cafe/parselglossy/releases/tag/v0.6.0
.. _0.5.0: https://github.com/dev-cafe/parselglossy/releases/tag/v0.5.0
.. _0.3.0: https://github.com/dev-cafe/parselglossy/releases/tag/v0.3.0
.. _0.3.0-alpha2: https://github.com/dev-cafe/parselglossy/releases/tag/v0.3.0-alpha2
.. _0.3.0-alpha1: https://github.com/dev-cafe/parselglossy/releases/tag/v0.3.0-alpha1
.. _0.2.0: https://github.com/dev-cafe/parselglossy/releases/tag/v0.2.0
.. _0.1.0: https://pypi.org/project/parselglossy/0.1.0/
.. _Getkw: https://github.com/dev-cafe/libgetkw
