import pytest

from web_pyoctopus.api import OctopusAPI


@pytest.fixture
def api():
    return OctopusAPI()


@pytest.fixture
def client(api):
    return api.test_session()
