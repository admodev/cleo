import os

import pytest


@pytest.fixture()
def environ():
    current_environ = os.environ.copy()

    yield

    os.environ = current_environ
