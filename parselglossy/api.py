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

# -*- coding: utf-8 -*-
"""Top-level functions for parselglossy."""

import json
from pathlib import Path
from typing import Union

from .grammars import lexer
from .utils import ComplexEncoder, JSONDict, as_complex, path_resolver, read_yaml_file
from .validation import validate_from_dicts


def lex(
    *, infile: Union[str, Path], grammar: str, ir_file: Union[str, Path] = None
) -> JSONDict:
    """Run grammar of choice on input string.

    Parameters
    ----------
    in_str : IO[Any]
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
        ir = lexer.lex_from_str(in_str=f, grammar=grammar, ir_file=ir_file)

    return ir


def validate(
    *,
    infile: Union[str, Path],
    fr_file: Union[str, Path] = None,
    template: Union[str, Path]
) -> JSONDict:
    """Validate intermediate representation into final representation.

    Parameters
    ----------
    infile : Union[str, Path]
        The file with the intermediate representation (JSON format).
    fr_file : Union[str, Path]
        File to write final representation to (JSON format).
        None by default, which means file is not written out.
    template : Union[str, Path]
        Which validation template to use.
    """

    infile = path_resolver(infile)
    with infile.open("r") as f:
        ir = json.load(f, object_hook=as_complex)

    template = path_resolver(template)
    stencil = read_yaml_file(Path(template))

    if fr_file is not None:
        fr_file = path_resolver(fr_file)

    fr = validate_from_dicts(ir=ir, template=stencil, fr_file=fr_file)

    return fr


def parse(
    *,
    infile: Union[str, Path],
    outfile: Union[str, Path] = None,
    grammar: str,
    template: Union[str, Path],
    dump_ir: bool = False
) -> None:
    """Parse input file.

    Parameters
    ----------
    infile : Union[str, Path]
        The input file to be parsed.
    outfile : Union[str, Path]
        The output file.
        None by default, which means file name default to <infile>_fr.json
    grammar : str
        Which grammar to use.
    template : Union[str, Path]
        Which validation template to use.
    write_ir_out : bool
        Whether to write out the intermediate representation to file (JSON format).
        False by default. If true the filename if <infile>_ir.json
    """

    stem = infile.rsplit(".", 1)[0]

    infile = path_resolver(infile)
    if dump_ir:
        ir_file = path_resolver(stem + "_ir.json")
    else:
        ir_file = None

    ir = lex(infile=infile, outfile=ir_file, grammar=grammar)

    template = path_resolver(template)

    fr = validate(infile=ir_file, outfile=outfile, template=template)

    if outfile is not None:
        outfile = path_resolver(stem + "_fr.json")
        with outfile.open("w") as out:
            json.dump(fr, out, cls=ComplexEncoder)
