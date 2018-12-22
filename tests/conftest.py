from io import StringIO

import pytest


def pytest_namespace():
    return {'getkw_keywords_json': StringIO()}
