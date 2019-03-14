#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pprint
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import yaml
from parselglossy import exceptions

JSONDict = Dict[str, Any]

pp = pprint.PrettyPrinter(indent=4)


def read_yaml_file(file_name: Path) -> Dict[str, Any]:
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
    with file_name.open('r') as f:
        try:
            d = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)
    return d


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
    if what not in ['keyword', 'section']:
        raise ValueError('Only \'keyword\' or \'section\' are valid values for parameter \'what\'')

    whats = '{:s}s'.format(what)
    if whats in template_dict:
        # Map `Callable` onto collecion, filter out `None` from the resulting list
        stuff = list(filter(None, map(how, template_dict[whats])))
    else:
        stuff = []

    return stuff


def old_decimate(d: JSONDict) -> JSONDict:
    # TODO Make sure that keywords have type and documentation
    # TODO Make sure that sections have documentation

    # Put None where there is nothing. Should come in handy for checking reasonable defaults
    # TODO there needs to be another pass at defaulting, as it might actually be a callable
    defaults = {v['name']: v['default'] if 'default' in v else None for v in d['keywords']}

    # We defer type checking and coercion till after we have merge the defaults with the user input
    # Type coercion means using the specified type for a type cast, however, given that we allow callables
    # as defaults, we might want to finesse that as type(callable(input_dict))

    types = {v['name']: v['type'] if 'type' in d['keywords'] else exceptions.SpecificationError for v in d['keywords']}

    docstrings = {
        v['name']: v['docstring']
        if 'docstring' in d['keywords'] and v['docstring'].strip() != '' else exceptions.SpecificationError
        for v in d['keywords']
    }

    predicates = {v['name']: v['predicates'] if 'predicates' in d['keywords'] else None for v in d['keywords']}

    # Commence the recursive descent, if we have sections, that is!
    if 'sections' in d:
        for section in d['sections']:
            defaults[section['name']] = old_decimate(section)

    return defaults  # {'defaults': defaults, 'types': types, 'docstrings': docstrings, 'predicates': predicates}


def view_by(what: str,
            d: Dict[str, Any],
            *,
            predicate: Callable[[Any, str], bool] = lambda x, y: True,
            missing: Union[None, Exception] = None,
            transformer: Callable[[Any], Any] = lambda x: x) -> JSONDict:
    """Recursive decimation of a template into an input.

    Parameters
    ----------
    what: str
    d: JSONDict
    predicate: Callable
       A predicate accepting one argument.
    missing: Union[None, Exception]
    transformer: Callable

    Notes
    -----
    Why don't we just throw an exception as soon as something goes wrong?
    For example, consider this pattern:

    .. code-block:: python
       view = {v['name']: transformer(v[what]) if all([what in v, predicate(v, what)]) else missing for v in d['keywords']}

    we could just embed in a ``try``-``except`` and catch it. However, we want
    to produce errors that are as informative as possible, hence we decide to
    keep track of what went wrong and raise only when validation is done.
    """

    view = {v['name']: transformer(v[what]) if all([what in v, predicate(v, what)])
            else missing for v in d['keywords']}

    if 'sections' in d:
        for section in d['sections']:
            view[section['name']] = view_by(what, section, predicate=predicate,
                                            missing=missing, transformer=transformer)

    return view


def apply_mask(incoming: JSONDict, mask: Dict[str, Callable[[Any], Any]]) -> JSONDict:
    """Apply a mask over a dictionary.

    Parameters
    ----------
    incoming: JSONDict
        Dictionary to be masked.
    mask: Dict[str, Callable[[Any], Any]]
        Mask to apply to `incoming`.

    Notes
    -----
    There are no checks on consistency of the structure of the two dictionaries.
    """

    return {k: mask[k](v) if not isinstance(v, dict) else apply_mask(v, mask[k]) for k, v in incoming.items()}


# Callbacks to coerce types
coerce_callbacks = {
    'bool': bool,
    # We remove spaces so the string-to-complex cast works without surprises
    'complex': lambda x: complex(x.replace(' ', '')),
    'float': float,
    'int': int,
    'str': str,
}
tmp = {'List[{:s}]'.format(k): lambda x: list(map(v, x)) for k, v in coerce_callbacks.items()}
coerce_callbacks.update(tmp)


def predicate_checker(incoming: Dict[str, Optional[List[str]]]) -> JSONDict:
    """Check that predicates are valid Python.

    Parameters
    ----------

    Returns
    -------
    """
    outgoing = {}
    for k, ps in incoming.items():
        if ps is None:
            outgoing[k] = None
        elif isinstance(ps, dict):
            outgoing[k] = predicate_checker(ps)
        else:
            outgoing[k] = []
            for p in ps:
                try:
                    outgoing[k].append(compile(p, '<unknown>', 'eval'))
                except SyntaxError:
                    outgoing[k].append(exceptions.SpecificationError(
                        'Python syntax error in predicate "{:s}"'.format(v)))

    return outgoing


if __name__ == "__main__":
    d = read_yaml_file(Path('tests/validation/overall/template.yml'))
    ds = old_decimate(d)
    pp.pprint(ds)

    types = view_by('type', d, missing=exceptions.SpecificationError, transformer=lambda x: coerce_callbacks[x])
    print('types')
    pp.pprint(types)

    # Get defaults and coerce their types
    defaults = apply_mask(view_by('default', d), types)
    print('defaults')
    pp.pprint(defaults)

    docstrings = view_by(
        'docstring', d, predicate=(lambda x, y: x[y].strip() != ''), missing=exceptions.SpecificationError)
    print('docstrings')
    pp.pprint(docstrings)

    predicates = view_by('predicates', d)
    print('predicates')
    pp.pprint(predicates)
    predicates = predicate_checker(predicates)
    pp.pprint(predicates)
