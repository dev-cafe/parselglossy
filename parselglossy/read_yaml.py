import yaml
from typing import Any, Dict


JSONDict = Dict[str, Any]


def read_yaml_file(file_name: str) -> JSONDict:
    """Reads a YAML file and returns it as a dictionary.
    """
    # convert to str() because
    # pathlib integrates nicely with open only for python >= 3.6
    with open(str(file_name), 'r') as f:
        try:
            d = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)
    return d
