from pathlib import Path

import yaml

from .utils import JSONDict


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
