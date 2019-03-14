=====
Usage
=====

To use parselglossy in a project::

    import parselglossy


Validation specifications
---------------------------

Possible fields for keywords are:

:`name`:
  The name of the keyword. Mandatory.
:`type`:
  Type of the corresponding value. Mandatory.
:`docstring`:
  A documentation string, possibly multiline. Mandatory.
:`default`:
  The default value. It can be a value of the declared type or a callable.
  The callable can be used to compute default values based on the default
  value of any other keyword in the input. If absent, the keyword is
  required, meaning that the user will have to supply it in their own
  input.
:`predicates`:
  A list of callables to sanity-check the passed value. Note that type checking is
  always performed automatically.

Possible fields for sections are:

:`name`:
   The name of the section. Mandatory.
:`docstring`:
   A documentation string, possibly multiline. Mandatory.
:`keywords`:
   A list of keywords belonging to the section.
:`sections`:
   A list of sections belonging to the section.

One or both of `keywords` and `sections` **must** be present.
