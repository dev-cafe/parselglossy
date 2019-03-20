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


class ParselglossyError(Exception):
    """Exception raised when parsing fails."""

    pass


class Error(namedtuple("Error", ["address", "message"], defaults=[(), ""])):
    """Detailed error reporting for dictionaries.

    Attributes
    ----------
    address : Tuple
         The keys needed to access the offending element in the `dict`.
    message : str
         The error message.
    """

    __slots__ = ()

    def __repr__(self):
        msg = "{:s}".format(self.message)
        if self.address != ():
            msg = "At {:s}:\n  {:s}".format(
                reduce(lambda x, y: x + "['{}']".format(y), self.address, "user"), msg
            )
        return "- " + msg


def collate_errors(*, when: str, errors: List[Error]) -> str:
    """Collate a list of error into an informative message.

    Parameters
    ----------
    when: str
        When the error occurred.
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
    preamble = "\nError{more:s} occurred when {when:s}:".format(
        more="(s)" if len(errors) > 1 else "", when=when
    )
    msgs = [preamble] + ["{}".format(e) for e in errors]

    return "\n".join(msgs)
