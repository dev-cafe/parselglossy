# -*- coding: utf-8 -*-
#
# parselglossy -- Generic input parsing library, speaking in tongues
# Copyright (C) 2019 Roberto Di Remigio, Radovan Bast, and contributors.
#
# This file is part of parselglossy.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# For information on the complete list of contributors to the
# parselglossy library, see: <http://parselglossy.readthedocs.io/>
#

"""Top-level functions for parselglossy."""

import json
from pathlib import Path
from typing import List, Optional, Union
from pyparsing import __file__ as ppfile

from .exceptions import ParselglossyError
from .documentation import documentation_generator
from .grammars import lexer
from .utils import JSONDict, as_complex, path_resolver, copier
from .yaml_utils import read_yaml_file
from .validation import is_template_valid, validate_from_dicts
from . import generation


def generate(
    template: Union[str, Path],
    *,
    where: Union[str, Path] = Path.cwd() / "input_parser",
    grammar: Union[str, Path, List[Path]] = "standard",
    docfile: str = "input.rst",
) -> None:
    """Generate parser for client.

    Parameters
    ----------
    template : Union[str, Path]
        Which validation template to use.
    where : Union[str, Path]
        Where to generate the parsing module. Default to `input_parser` folder
        under current working directory.
    grammar : Union[str, Path, List[Path]]
        The file containing the grammar to use to tokenize user input.
        Defaults to `standard`, *i.e.* use one of the grammars packaged with
        the library.
    docfile : str
        The name of the documentation file for the input.
        Defaults to `input.rst`.

    Notes
    -----
    This function will generate a Python module for parsing inputs as defined
    by the template and grammar provided as parameters.

    The user can provide a grammar as (a list of) external file(s).
    The function performing tokenization **must return** an object of
    ``Dict[str, Any]`` type: a, potentially recursive, dictionary of keys and
    values.
    It is the responsibility of the user to satisfy any dependencies of the
    parsing grammar they provided.

    Raises
    ------
    :exc:`ParselglossyError`
    """
    where_ = path_resolver(where, touch=False)

    # Create plumbing subfolder
    (where_ / "plumbing").mkdir(parents=True, exist_ok=True)
    # Generate __init__.py
    with (where_ / "__init__.py").open("w") as f:
        f.write(generation.INIT_PY)
    # Generate README.md
    with (where_ / "README.md").open("w") as f:
        f.write(generation.README)
    # Copy files
    # a. pyparsing.py
    copier(ppfile, where_ / "plumbing")
    # b. copy exceptions.py, types.py, utils.py, validation.py,
    # validation_plumbing.py, views.py file
    for fname in [
        "exceptions",
        "types",
        "utils",
        "validation",
        "validation_plumbing",
        "views",
    ]:
        copier(Path(__file__).parent.absolute() / f"{fname}.py", where_ / "plumbing")
    # c. Copy the grammar.
    # By default this is our standard grammar, but could be one file provided
    # by the user. The file is called "grammar.py"
    if isinstance(grammar, str):
        if grammar not in ["standard", "getkw"]:
            raise ParselglossyError(f"Grammar {grammar} not available.")
        # copy atoms.py
        copier(
            Path(__file__).parent.absolute() / "grammars/atoms.py", where_ / "plumbing",
        )
        # copy getkw.py
        copier(
            Path(__file__).parent.absolute() / "grammars/getkw.py",
            where_ / "plumbing/grammar.py",
        )
        if grammar == "standard":
            lexer_str = "grammar.grammar(has_complex=True)"
        else:
            lexer_str = "grammar.grammar(has_complex=False)"
    elif isinstance(grammar, Path):
        copier(grammar.resolve(), where_ / "plumbing/grammar.py")
        lexer_str = "grammar.grammar()"
    elif isinstance(grammar, list):
        for _ in grammar:
            copier(_.resolve(), where_ / "plumbing")
            lexer_str = "grammar.grammar()"
    else:
        raise ParselglossyError("Type not recognized for grammar")


    # d. generate lexer.py
    # NOTE I am assuming the grammar defined outside defines the same API as
    # our own.
    # TODO Document the above fact!
    with (where_ / "plumbing/lexer.py").open("w") as f:
        f.write(generation.lexer_py(lexer_str))

    # Generate api.py
    template_ = path_resolver(template, touch=False)
    stencil = read_yaml_file(template_)

    # Check if the template is valid
    is_template_valid(stencil)

    with (where_ / "api.py").open("w") as f:
        f.write(generation.api_py(stencil))
    # Generate cli.py (uses argparse)
    with (where_ / "cli.py").open("w") as f:
        f.write(generation.CLI_PY)
    # Generate documentation
    (where_ / "docs").mkdir(parents=True, exist_ok=True)
    docs = documentation_generator(stencil, header="Input parameters")
    outfile = path_resolver(where_ / f"docs/{docfile}")
    with outfile.open("w") as o:
        o.write(docs)


def lex(
    infile: Union[str, Path],
    grammar: str = "standard",
    ir_file: Optional[Union[str, Path]] = None,
) -> JSONDict:
    """Run grammar of choice on input string.

    Parameters
    ----------
    infile : Union[str, Path]
        The string to be parsed.
    grammar : str
        Grammar to be used.
    ir_file : Union[str, Path]
        File to write intermediate representation to (JSON format).
        None by default, which means file is not written out.

    Returns
    -------
    The contents of the input string as a dictionary.
    """

    infile = path_resolver(infile)
    if ir_file is not None:
        ir_file = path_resolver(ir_file)

    with infile.open("r") as f:
        ir = lexer.lex_from_str(in_str=f.read(), grammar=grammar, ir_file=ir_file)

    return ir


def validate(
    infile: Union[str, Path],
    template: Union[str, Path],
    fr_file: Optional[Union[str, Path]] = None,
) -> JSONDict:
    """Validate intermediate representation into final representation.

    Parameters
    ----------
    infile : Union[str, Path]
        The file with the intermediate representation (JSON format).
    template : Union[str, Path]
        Which validation template to use.
    fr_file : Union[str, Path]
        File to write final representation to (JSON format).
        None by default, which means file is not written out.

    Returns
    -------
    The validated input as a dictionary.
    """

    infile = path_resolver(infile)
    with infile.open("r") as f:
        ir = json.load(f, object_hook=as_complex)

    template = path_resolver(template)
    stencil = read_yaml_file(template)

    if fr_file is not None:
        fr_file = path_resolver(fr_file)

    return validate_from_dicts(ir=ir, template=stencil, fr_file=fr_file)


def parse(
    infile: Union[str, Path],
    template: Union[str, Path],
    outfile: Optional[Union[str, Path]] = None,
    grammar: str = "standard",
    dump_ir: bool = False,
) -> JSONDict:
    """Parse input file.

    Parameters
    ----------
    infile : Union[str, Path]
        The input file to be parsed.
    template : Union[str, Path]
        Which validation template to use.
    outfile : Optional[Union[str, Path]]
        The output file.
        Defaults to ``None``, which means writing to ``<infile>_fr.json``.
    grammar : str
        Which grammar to use. Defaults to ``standard``.
    dump_ir : bool
        Whether to write out the intermediate representation to file (JSON format).
        False by default. If true the filename if ``<infile>_ir.json``

    Returns
    -------
    The validated input as a dictionary.
    """

    infile = path_resolver(infile)

    ir_file = None  # type: Optional[Path]
    if dump_ir:
        ir_file = path_resolver(Path(infile).stem + "_ir.json")

    ir = lex(infile=infile, ir_file=ir_file, grammar=grammar)

    template = path_resolver(template)
    stencil = read_yaml_file(template)

    if outfile is not None:
        outfile = path_resolver(outfile)

    return validate_from_dicts(ir=ir, template=stencil, fr_file=outfile)


def document(
    template: Union[str, Path],
    outfile: Optional[Union[str, Path]] = None,
    header: str = "Input parameters",
) -> str:
    """Generate documentation in reStructuredText format from validation template.

    Parameters
    ----------
    template : Union[str, Path]
        Which validation template to use.
    output : Union[str, Path]
        Where to save the generated documentation.
        Defaults to ``None``.
    header : str
        Header for the documentation page.
        Defaults to ``Input parameters``.

    Returns
    -------
    The documentation page as a string.
    """

    template = path_resolver(template)
    stencil = read_yaml_file(template)

    is_template_valid(stencil)

    docs = documentation_generator(stencil, header=header)

    if outfile is not None:
        outfile = path_resolver(outfile)
        with outfile.open("w") as o:
            o.write(docs)

    return docs
