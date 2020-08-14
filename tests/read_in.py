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


"""Facilities for reading in files for testing."""

from pathlib import Path
from typing import Optional, Tuple, Union

from parselglossy.utils import JSONDict
from parselglossy.yaml_utils import read_yaml_file


def read_in(
    category: Union[str, Path], input_file_name: Optional[str], template_file_name: str
) -> Tuple[JSONDict, JSONDict]:
    """Helper function to read in input and validation template

    Parameters
    ----------
    category: str
    input_file_name: Optional[str]
    template_file_name: str

    Returns
    -------
    input_dict, template_dict: Tuple[JSONDict, JSONDict]
         A tuple with the two dictionaries.
    """
    this_path = Path(__file__).parent

    if input_file_name is None:
        input_dict = {}  # type: JSONDict
    else:
        input_file = this_path / "validation" / category / input_file_name
        input_dict = read_yaml_file(input_file)

    template_file = this_path / "validation" / category / template_file_name
    template_dict = read_yaml_file(template_file)

    return input_dict, template_dict
