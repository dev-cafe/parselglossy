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
from typing import IO, Any, Optional, Union

from . import getkw
from ..exceptions import ParselglossyError
from ..utils import ComplexEncoder, JSONDict, path_resolver


def lex_from_str(
    *,
    in_str: IO[Any],
    grammar: str = "standard",
    ir_file: Optional[Union[str, Path]] = None
) -> JSONDict:
    """Run grammar of choice on input string.

    Parameters
    ----------
    in_str : IO[Any]
         The string to be parsed.
    grammar : str
         Grammar to be used. Defaults to "standard".
    ir_file : Union[str, Path]
         File to write intermediate representation to (JSON format).
         None by default, which means file is not written out.

    Returns
    -------
    The contents of the input string as a dictionary.

    Raises
    ------
    :exc:`ParselglossyError`
    """

    try:
        lexer = dispatch_grammar(grammar)
    except KeyError:
        raise ParselglossyError("Grammar {} not available.".format(grammar))

    ir = lexer.parseString(in_str).asDict()

    if ir_file is not None:
        ir_file = path_resolver(ir_file)
        with ir_file.open("w") as out:
            json.dump(ir, out, cls=ComplexEncoder, indent=4)

    return ir


def dispatch_grammar(grammar: str):
    available_grammars = {
        "getkw": getkw.grammar(),
        "standard": getkw.grammar(has_complex=True),
    }
    return available_grammars[grammar]
