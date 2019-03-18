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
"""Error-handling facilities."""

from collections import namedtuple
from functools import reduce
from typing import List


class ValidationError(Exception):
    """Exception raised for invalid input files."""

    pass


class SpecificationError(Exception):
    """Exception raised for malformed validation template."""

    pass


Error = namedtuple("Error", ["address", "message"])


def collate_errors(errors: List[Error]) -> str:
    """Collate a list of error into an informative message.

    Parameters
    ----------
    errors: List[Error]
        List of errors.

    Returns
    -------
    msg: str
        An error message with details about where in the dictionary the error
        arose and what the error is. For example::

            Error(s) occurred when fixing defaults:
            - At 'user['scf']['another_number']'
                KeyError 'min_num_iterations' in defaulting closure
                'user['scf']['min_num_iterations'] / 2'
    """
    msgs = ["\nError(s) occurred when fixing defaults:"]
    msgs.extend(
        [
            "- At {:s}:\n    {:s}".format(
                reduce(lambda x, y: x + "['{}']".format(y), e.address, "user"),
                e.message,
            )
            for e in errors
        ]
    )

    return "\n".join(msgs)
