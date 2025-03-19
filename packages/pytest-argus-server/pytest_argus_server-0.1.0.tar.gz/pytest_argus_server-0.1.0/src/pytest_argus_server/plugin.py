import os
from urllib.parse import urljoin

import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

pytest_plugins = ["pytest_docker_compose"]
TEST_PASSWORD = "fakef00bar"


def pytest_addoption(parser):
    group = parser.getgroup("argus-server")
    group.addoption(
        "--argus-version",
        action="store",
        dest="argus_version",
        default="latest",
        help="Set the version of the Argus API server to run",
    )


@pytest.fixture(scope="session")
def argus_version(request):
    version = request.config.option.argus_version
    os.environ["ARGUS_VERSION"] = version
    return version


@pytest.fixture(scope="session")
def argus_api(wait_for_argus_api):
    """Returns the URL and a valid token for a running Argus API server"""

    request_session, container = wait_for_argus_api
    container.execute(["django-admin", "initial_setup"])
    container.execute(["django-admin", "setpassword", "admin", TEST_PASSWORD])

    service = container.network_info[0]
    argus_url = f"http://127.0.0.1:{service.host_port}/"

    response = request_session.post(
        urljoin(argus_url, "/api/v1/token-auth/"),
        data={"username": "admin", "password": TEST_PASSWORD},
    )
    token = response.json().get("token", None)
    assert token, f"Failed to get token from {response.payload}"

    return "http://localhost:8000/api/v2", token


@pytest.fixture(scope="session")
def wait_for_argus_api(argus_version, session_scoped_container_getter):
    """Wait for an Argus API server to become responsive.

    :returns: A tuple of the request session used to test for connectivity and an
    object representing the API container instance
    """
    request_session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    request_session.mount("http://", HTTPAdapter(max_retries=retries))

    container = session_scoped_container_getter.get("argus_api")
    service = container.network_info[0]
    argus_url = f"http://127.0.0.1:{service.host_port}/"
    print(f"Attempting to connect to {argus_url}")
    assert request_session.get(argus_url)
    return request_session, container
