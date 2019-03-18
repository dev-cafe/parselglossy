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

import re
from typing import Callable, List, Union

from .exceptions import SpecificationError, ValidationError
from .utils import JSONDict

AllowedTypes = Union[
    bool,
    str,
    int,
    float,
    complex,
    List[bool],
    List[str],
    List[int],
    List[float],
    List[complex],
]


def merge_ours(*, theirs: JSONDict, ours: JSONDict) -> JSONDict:
    """Recursively merge two `dict`-s with "ours" strategy.

    Parameters
    ----------
    theirs: JSONDict
    ours: JSONDict

    Returns
    -------
    outgoing: JSONDict

    Notes
    -----
    The `theirs` dictionary is supposed to be the view by defaults of the
    validation specification, whereas `ours` is the dictionary from user input.
    The recursive merge action will generate a complete, but not validated,
    input dictionary by using default values where these are not overridden by
    user input, hence the naming "ours" for the merge strategy.
    """
    outgoing = {}

    for k, v in theirs.items():
        if isinstance(v, dict):
            outgoing[k] = merge_ours(theirs=v, ours=ours[k])
        elif k not in ours.keys():
            outgoing[k] = theirs[k]
        else:
            outgoing[k] = ours[k]

    return outgoing


def type_matches(value: AllowedTypes, expected_type: str) -> bool:
    """Checks whether a value is of the expected type.

    Parameters
    ----------
    value: Any
      Value whose type needs to be checked
    expected_type: AllowedTypes

    Notes
    -----
    Allowed types T are: `str`, `int`, `float`, `complex`, `bool`,
    as well as `List[T]`.

    Returns
    -------
    True if value has the type expected_type, otherwise False.

    Raises
    ------
    ValueError
        If expected_type is not among the allowed types.
    """
    allowed_basic_types = ["str", "int", "float", "complex", "bool"]
    allowed_list_types = ["List[{}]".format(t) for t in allowed_basic_types]
    allowed_types = allowed_basic_types + allowed_list_types

    # first verify whether expected_type is allowed
    if expected_type not in allowed_types:
        raise ValueError("could not recognize expected_type: {}".format(expected_type))

    expected_type_is_list = re.search(r"^List\[(\w+)\]$", expected_type)

    if expected_type_is_list is not None:
        # make sure that value is actually a list
        if not type(value).__name__ == "list":
            return False

        # iterate over each element of the list
        # and check whether it matches T
        return all((type(x).__name__ == expected_type_is_list.group(1) for x in value))
    else:
        # expected type is a basic type
        # this is the simpler case
        return type(value).__name__ == expected_type


def extract_from_template(what: str, how: Callable, template_dict: JSONDict) -> List:
    """Extract from a template dictionary.

    Parameters
    ----------
    what: str
        Determines what to extract: either `keyword` or `section`.
    how: Callable
        Determines how to extract from `template_dict`.
    template_dict: JSONDict
        Contains the input template.

    Returns
    -------
    stuff: List
         List containing `what` you wanted extracted `how` you wanted.
    """
    if what not in ['keywords', 'sections']:
        raise ValueError('Only \'keywords\' or \'sections\' are valid values for parameter \'what\'')

    if what in template_dict:
        # Map `Callable` onto collecion, filter out `None` from the resulting list
        stuff = list(filter(None, map(how, template_dict[what])))
    else:
        stuff = []

    return stuff


def undocumented(x) -> bool:
    return (True if 'docstring' not in x or x['docstring'].strip() == '' else False)


def validate_node(input_dict: JSONDict, template_dict: JSONDict) -> JSONDict:
    """Validate a node.

    A node is either the root of the input or it is a section.  The node can
    contain keywords or other sections which we traverse recursively.

    Parameters
    ----------
    input_dict: JSONDict
        Contains the input to be checked.
    template_dict: JSONDict
        Contains the input template to be checked against.

    Returns
    -------
    input_dict: JSONDict
        This function modifies input_dict (e.g. fills in defaults).

    Raises
    ------
    ValidationError
        This signals an error in the input that is to be parsed.
    SpecificationError
        This signals an error in the input template.
    """
    template_sections = extract_from_template('sections', lambda x: x['name'], template_dict)
    sections_no_doc = extract_from_template('sections', lambda x: x['name'] if undocumented(x) else None,
                                            template_dict)
    template_keywords = extract_from_template('keywords', lambda x: x['name'], template_dict)
    keywords_no_doc = extract_from_template('keywords', lambda x: x['name'] if undocumented(x) else None,
                                            template_dict)

    # stop if we find a section or keyword without documentation
    if sections_no_doc:
        raise SpecificationError(
            "section(s) without any documentation: {}".format(sections_no_doc)
        )
    if keywords_no_doc:
        raise SpecificationError(
            "keyword(s) without any documentation: {}".format(keywords_no_doc)
        )

    input_sections = [x for x in input_dict if isinstance(input_dict[x], dict)]
    input_keywords = list(filter(lambda x: x not in input_sections, input_dict.keys()))

    # make sure that we did not receive keywords
    # or sections which we did not expect
    difference = set(input_keywords).difference(set(template_keywords))
    if difference != set():
        raise ValidationError("found unexpected keyword(s): {}".format(difference))
    difference = set(input_sections).difference(set(template_sections))
    if difference != set():
        raise ValidationError("found unexpected section(s): {}".format(difference))

    # check that keywords without a default are set in the input
    keywords_no_default = [x['name'] for x in template_dict['keywords'] if 'default' not in x]
    difference = set(keywords_no_default).difference(set(input_keywords))
    if difference != set():
        raise ValidationError(
            "the following keyword(s) must be set: {}".format(difference)
        )

    # for each keyword verify the type of the value
    for keyword in input_keywords:
        template_keyword = list(filter(lambda x: x['name'] == keyword, template_dict['keywords']))[0]
        _type = template_keyword['type']
        if not type_matches(input_dict[keyword], _type):
            raise ValidationError(
                "incorrect type for keyword: '{0}', expected '{1}' type".format(
                    keyword, _type
                )
            )

    # fill missing input keywords with template defaults
    for keyword in set(template_keywords).difference(set(input_keywords)):
        template_keyword = list(filter(lambda x: x['name'] == keyword, template_dict['keywords']))[0]
        _default = template_keyword['default']
        input_dict[keyword] = _default

    # if this node contains sections, we descend into these and verify these in turn
    for section in template_sections:
        input_section = input_dict[section]
        template_section = list(filter(lambda x: x['name'] == section, template_dict['sections']))[0]
        input_dict[section] = validate_node(input_section, template_section)

    return input_dict


def check_predicates_node(
    input_dict: JSONDict, input_dict_node: JSONDict, template_dict_node: JSONDict
) -> None:
    """Check keyword predicates in a node.

    A node is either the root of the input or it is a section.  The node can
    contain keywords or other sections which we traverse recursively.

    This function does not modify input arguments.

    Parameters
    ----------
    input_dict: JSONDict
        Contains the entire input tree.
    input_dict_node: JSONDict
        Contains the input to be checked: only current node.
    template_dict: JSONDict
        Contains the input template which holds the predicates.

    Raises
    ------
    ValidationError
        This signals an error in the input that is to be parsed.
    SpecificationError
        This signals an error in the input template.
    """
    input_sections = [
        x for x in input_dict_node if type(input_dict_node[x]).__name__ == "dict"
    ]
    input_keywords = list(
        filter(lambda x: x not in input_sections, input_dict_node.keys())
    )

    if 'sections' in template_dict_node:
        template_sections = [x['name'] for x in template_dict_node['sections']]
    else:
        template_sections = []

    # go through the predicates
    for keyword in input_keywords:
        template_keyword = list(filter(lambda x: x['name'] == keyword, template_dict_node['keywords']))[0]
        # this value is used by eval() so we skip E841 warning of flake8
        value = input_dict_node[keyword]  # noqa
        if "predicates" in template_keyword:
            for predicate in template_keyword["predicates"]:
                try:
                    r = eval(predicate)
                except (SyntaxError, NameError):
                    raise SpecificationError(
                        "error in predicate '{}' in keyword '{}'".format(
                            predicate, keyword
                        )
                    )
                if not r:
                    raise ValidationError(
                        'predicate "{}" failed in keyword "{}"'.format(
                            predicate, keyword
                        )
                    )

    # if this node contains sections, we descend into these and verify these in turn
    for section in template_sections:
        input_section = input_dict_node[section]
        template_section = list(filter(lambda x: x['name'] == section, template_dict_node['sections']))[0]
        check_predicates_node(input_dict, input_section, template_section)
