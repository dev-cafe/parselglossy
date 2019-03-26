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
"""Common utilities."""

import json
from functools import reduce
from pathlib import Path
from string import ascii_letters, digits
from typing import Any, Dict, Tuple, Union

import yaml

JSONDict = Dict[str, Any]

truthy = ["TRUE", "ON", "YES", "Y"]
"""List[str]: List of true-like values."""
falsey = ["FALSE", "OFF", "NO", "N"]
"""List[str]: List of false-like values."""

printable = ascii_letters + digits + r"!#$%&*+-./:;<>?@^_|~"
"""str: Custom printable character set.

The printable character set is the standard set in `string.printable` minus
"\'(),=[\\]`{} and all whitespace characters.
"""


class ComplexEncoder(json.JSONEncoder):
    """JSON encoder for complex numbers."""

    def default(self, obj):
        if isinstance(obj, complex):
            return {"__complex__": [obj.real, obj.imag]}
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def as_complex(dct):
    """JSON decoder for complex numbers."""
    if "__complex__" in dct:
        return complex(dct["__complex__"][0], dct["__complex__"][1])
    return dct


def location_in_dict(*, address: Tuple, dict_name: str = "user") -> str:
    """Convert tuple of keys of a ``JSONDict`` to its representation in code.

    For example, given ``("a", "b", "c")`` returns the string ``user['a']['b']['c']``.

    Parameters
    ----------
    address : Tuple[str]
    dict_name : str

    Returns
    -------
    where : str
    """
    return reduce(lambda x, y: x + "['{}']".format(y), address, "user")


def path_resolver(f: Union[str, Path]) -> Path:
    """Resolve a path.

    Parameters
    ----------
    f : Union[str, Path]
        File whose path needs to be resolved.

    Returns
    -------
    path : Path
        File as a ``Path`` object.

    Notes
    -----
    The file will be created if not already existent.
    """

    path = Path(f) if isinstance(f, str) else f

    if not path.exists():
        path.touch()

    return path.resolve()


def default_outfile(*, fname: Union[str, Path], suffix: str) -> str:
    """Default name for output file.

    Parameters
    ----------
    fname : Union[str, Path]
        Name to use as stencil.
    suffix : str
        Suffix to append.

    Returns
    -------
    The name of the output file.
    """
    fname = Path(fname) if isinstance(fname, str) else fname

    base = fname.name

    return base.rsplit(".", 1)[0] + suffix


def read_yaml_file(file_name: Path) -> JSONDict:
    """Reads a YAML file and returns it as a dictionary.

    Parameters
    ----------
    file_name: Path
        Path object for the YAML file.

    Returns
    -------
    d: JSONDict
        A dictionary with the contents of the YAML file.
    """
    with file_name.open("r") as f:
        try:
            d = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)
    return d
