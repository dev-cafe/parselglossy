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

from .utils import ComplexEncoder, JSONDict
from .validation import (
    check_predicates,
    fix_defaults,
    is_template_valid,
    merge_ours,
    typenade,
)
from .views import view_by_default, view_by_predicates, view_by_type


def validate(*, dumpfr: bool, ir: JSONDict, template: JSONDict) -> JSONDict:
    """Validate intermediate representation into final representation.

    Parameters
    ----------
    dumpir : bool
        Whether to serialize FR to JSON. Location and name of file are
        determined based on the input file.
    ir : JSONDict
        Intermediate representation of the input file.

    Returns
    -------
    fr : JSONDict
        The validated input.

    Raises
    ------
    :exc:`ParselglossyError`
    """
    template_ok = is_template_valid(template)
    stencil = view_by_default(template)
    types = view_by_type(template)
    predicates = view_by_predicates(template)

    fr = merge_ours(theirs=stencil, ours=ir)
    fr = fix_defaults(fr, types=types)
    fr = typenade(fr, types=types)
    predicates_ok = check_predicates(fr, predicates=predicates)

    if dumpfr:
        outfile = Path("validated.json")
        with outfile.open("w") as outfile:
            json.dump(fr, outfile, cls=ComplexEncoder)

    return fr
