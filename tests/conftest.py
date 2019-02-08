from io import StringIO

import pytest


def pytest_configure():
    pytest.getkw_keywords_json = StringIO()
