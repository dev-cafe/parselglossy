import os
from pathlib import Path
from parselglossy.validate import validate_node, check_predicates_node
from parselglossy.read_yaml import read_yaml_file
from typing import Dict, Any


JsonDict = Dict[str, Any]


def _helper(category: str,
            input_file_name: str,
            template_file_name: str) -> JsonDict:
    this_path = Path(os.path.dirname(os.path.realpath(__file__)))

    input_file = this_path / 'validation' / category / input_file_name
    template_file = this_path / 'validation' / category / template_file_name

    input_dict = read_yaml_file(input_file)
    template_dict = read_yaml_file(template_file)

    # checks everything except predicates
    input_dict = validate_node(input_dict, template_dict)

    # now that all keywords have some value, we can check predicates
    check_predicates_node(input_dict, input_dict, template_dict)

    return input_dict


def test_validation():
    input_dict = _helper('overall',
                         'input.yml',
                         'template.yml')

    reference = {
        'title': 'this is an example',
        'scf': {
            'functional': 'B3LYP',
            'max_num_iterations': 20,
            'some_acceleration': True,
            'thresholds': {
                 'some_integral_screening': 0.0002,
                 'energy': 1e-05
             },
            'another_number': 10,
            'some_complex_number': '0.0+0.0j'
        }
    }

    assert input_dict == reference
