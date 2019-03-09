import yaml
import os
from pathlib import Path
from parselglossy.validate import validate_node, check_predicates_node


def _read_yaml_file(file_name: str) -> str:
    '''
    Reads a YAML file and returns it as a dictionary.
    '''
    with open(file_name, 'r') as f:
        try:
            d = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)
    return d


def test_validation():
    this_path = Path(os.path.dirname(os.path.realpath(__file__)))

    input_file = this_path / 'validation' / 'example.yml'
    template_file = this_path / 'validation' / 'template.yml'

    input_dict = _read_yaml_file(input_file)
    template_dict = _read_yaml_file(template_file)

    # checks everything except predicates
    input_dict = validate_node(input_dict, template_dict)

    # now that all keywords have some value, we can check predicates
    check_predicates_node(input_dict, input_dict, template_dict)

#   print(input_dict)
