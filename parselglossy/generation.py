# -*- coding: utf-8 -*-
#
# parselglossy -- Generic input parsing library, speaking in tongues
# Copyright (C) 2020 Roberto Di Remigio, Radovan Bast, and contributors.
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

"""Constants used by the generator."""

from datetime import date
from pathlib import Path
from re import DOTALL, search

INIT_PY = f"""# -*- coding: utf-8 -*-

# This file was automatically generated by parselglossy on {date.today()}
# Editing is *STRONGLY DISCOURAGED*
"""
"""str: Content of generated __init__.py"""

README = f"""This file was automatically generated by parselglossy on {date.today()}
Editing is *STRONGLY DISCOURAGED*
"""
"""str: Content of generated README.md"""


CLI_PY = f"""# -*- coding: utf-8 -*-

# This file was automatically generated by parselglossy on {date.today()}
# Editing is *STRONGLY DISCOURAGED*

import argparse

from .api import parse
from .plumbing.utils import default_outfile


def cli():
    cli = argparse.ArgumentParser()
    cli.add_argument("infile", help="the input file to parse")
    cli.add_argument(
        "--dump-ir",
        dest="dumpir",
        help="whether to dump intermediate representation to JSON",
        action="store_true",
        default=False,
    )
    cli.add_argument(
        "--outfile",
        dest="outfile",
        help="name or path for the parsed JSON output file",
        type=str,
        action="store",
    )

    args = cli.parse_args()

    if args.outfile is None:
        outfile = default_outfile(fname=args.infile, suffix="_fr.json")

    parse(infile=args.infile, dump_ir=args.dumpir, outfile=outfile)
"""
"""str: Content of generated cli.py"""


def get_parse_string_to_dict() -> str:
    with (Path(__file__).parent.absolute() / "grammars/lexer.py").open("r") as buf:
        m = search(
            r"\# ->->-> SNIP <-<-<-\n(.*)\n\# -<-<-< SNAP >->->-", buf.read(), DOTALL,
        )
    if m is not None:
        return f"""\n
from pathlib import Path
from typing import Union

from .exceptions import ParselglossyError
from .utils import JSONDict, flatten_list, dict_to_list


{m.group(1)}"""
    else:
        raise RuntimeError("Nothing extracted from lexer.py!")


def lexer_py(lexer_str: str) -> str:
    return f"""# -*- coding: utf-8 -*-

# This file was automatically generated by parselglossy on {date.today()}
# Editing is *STRONGLY DISCOURAGED*

import json
from pathlib import Path
from typing import Optional, Union

from .utils import ComplexEncoder, JSONDict, path_resolver


def lex_from_str(*,
                 in_str: Union[str, Path],
                 ir_file: Optional[Union[str, Path]] = None
) -> JSONDict:
    \"\"\"Run grammar on input string.

    Parameters
    ----------
    in_str : Union[str, Path]
         The string to be parsed.
    ir_file : Optional[Union[str, Path]]
         File to write intermediate representation to (JSON format).
         None by default, which means file is not written out.

    Returns
    -------
    The contents of the input string as a dictionary.
    \"\"\"

    {lexer_str}

    if ir_file is not None:
        ir_file = path_resolver(ir_file)
        with ir_file.open("w") as out:
            json.dump(ir, out, cls=ComplexEncoder, indent=4)

    return ir
"""


def api_py(stencil):
    return f"""# -*- coding: utf-8 -*-

# This file was automatically generated by parselglossy on {date.today()}
# Editing is *STRONGLY DISCOURAGED*

import json
from pathlib import Path
from typing import Optional, Union

from .plumbing import lexer
from .plumbing.utils import JSONDict, as_complex, path_resolver, copier
from .plumbing.validation import is_template_valid, validate_from_dicts


def lex(
    infile: Union[str, Path],
    ir_file: Optional[Union[str, Path]] = None,
) -> JSONDict:
    \"\"\"Run grammar of choice on input string.

    Parameters
    ----------
    infile : Union[str, Path]
        The string to be parsed.
    ir_file : Optional[Union[str, Path]]
        File to write intermediate representation to (JSON format).
        None by default, which means file is not written out.

    Returns
    -------
    The contents of the input string as a dictionary.
    \"\"\"

    infile = path_resolver(infile)
    if ir_file is not None:
        ir_file = path_resolver(ir_file)

    with infile.open("r") as f:
        ir = lexer.lex_from_str(in_str=f.read(), ir_file=ir_file)

    return ir


def validate(
    infile: Union[str, Path],
    fr_file: Optional[Union[str, Path]] = None,
) -> JSONDict:
    \"\"\"Validate intermediate representation into final representation.

    Parameters
    ----------
    infile : Union[str, Path]
        The file with the intermediate representation (JSON format).
    fr_file : Optional[Union[str, Path]]
        File to write final representation to (JSON format).
        None by default, which means file is not written out.

    Returns
    -------
    The validated input as a dictionary.
    \"\"\"

    infile = path_resolver(infile)
    with infile.open("r") as f:
        ir = json.load(f, object_hook=as_complex)

    stencil = {stencil}

    if fr_file is not None:
        fr_file = path_resolver(fr_file)

    return validate_from_dicts(ir=ir, template=stencil, fr_file=fr_file)


def parse(
    infile: Union[str, Path],
    outfile: Optional[Union[str, Path]] = None,
    dump_ir: bool = False,
) -> JSONDict:
    \"\"\"Parse input file.

    Parameters
    ----------
    infile : Union[str, Path]
        The input file to be parsed.
    outfile : Optional[Union[str, Path]]
        The output file.
        Defaults to ``None``, which means writing to ``<infile>_fr.json``.
    dump_ir : bool
        Whether to write out the intermediate representation to file (JSON format).
        False by default. If true the filename if ``<infile>_ir.json``

    Returns
    -------
    The validated input as a dictionary.
    \"\"\"

    infile = path_resolver(infile)

    ir_file = None  # type: Optional[Path]
    if dump_ir:
        ir_file = path_resolver(Path(infile).stem + "_ir.json")

    ir = lex(infile=infile, ir_file=ir_file)

    stencil = {stencil}

    if outfile is not None:
        outfile = path_resolver(outfile)

    return validate_from_dicts(ir=ir, template=stencil, fr_file=outfile)
"""
