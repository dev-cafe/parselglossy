=======
History
=======

Unreleased_
-----------

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


.. _Unreleased: https://github.com/dev-cafe/parselglossy/compare/v0.3.0-alpha5...HEAD
.. _0.3.0-alpha2: https://github.com/dev-cafe/parselglossy/releases/tag/v0.3.0-alpha2
.. _0.3.0-alpha1: https://github.com/dev-cafe/parselglossy/releases/tag/v0.3.0-alpha1
.. _0.2.0: https://github.com/dev-cafe/parselglossy/releases/tag/v0.2.0
.. _0.1.0: https://pypi.org/project/parselglossy/0.1.0/
.. _Getkw: https://github.com/dev-cafe/libgetkw
