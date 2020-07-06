=====
Usage
=====

As a generator
--------------

parselglossy can be used to *generate* a parser for your project. This relieves
you and your users from depending on parselglossy itself for running your code.

Let us look at an example. We will assume your validation specification is in a
file ``template.yml`` and that your input conforms to the ``standard`` grammar
provided with parselglossy. You can then run the following command::

    parselglossy generate --target input_parser --template template.yml --grammar standard

You will notice a folder ``input_parser`` has been generated, with the following
contents::

    input_parser
    ├── api.py
    ├── cli.py
    ├── docs
    │   └── input.rst
    ├── __init__.py
    ├── plumbing
    │   ├── atoms.py
    │   ├── exceptions.py
    │   ├── getkw.py
    │   ├── lexer.py
    │   ├── pyparsing.py
    │   ├── types.py
    │   ├── utils.py
    │   ├── validation_plumbing.py
    │   ├── validation.py
    │   └── views.py
    └── README.md

This is a complete Python module containing the parser specific to your project.
This module only depends on functionality provided with any standard Python
installation: no need for additional dependencies!
The generator will copy files from parselglossy in the ``plumbing`` subfolder
and generate documentation in reStructuredText format. The two source files
``api.py`` and ``cli.py`` will be the most useful to actually use the generated
parser. The former exposes an API similar to that of parselglossy, the latter
defines a minimal argparse CLI on top of this API.
An interface to the generated parser would look as follows::

    from input_parser import cli

    cli.cli()

It is also possible to generate parser with grammars *outside* of what parselglossy provides.
In that case, you will need to invoke the ``generate`` subcommand with arguments:

- Listing all Python files defining your grammar::

    -g file1.py -g file2.py -g file3.py

- Giving the Python commands to use your grammar::

    --tokenize "import file1; ir = file1.command()"

  Note that the result of such a command **has** to be in a variable called ``ir``.

As a Python module
------------------

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
