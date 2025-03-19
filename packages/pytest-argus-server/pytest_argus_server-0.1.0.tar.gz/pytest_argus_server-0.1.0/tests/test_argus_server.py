import os

import pytest_argus_server


def test_version_fixture(pytester):
    """Make sure that pytest accepts our fixture."""

    # create a temporary pytest test module
    pytester.makepyfile("""
        def test_sth(argus_version):
            assert argus_version == "1.33.0"
    """)

    # run pytest with the following cmd args
    result = pytester.runpytest("--argus-version=1.33.0", "-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(
        [
            "*::test_sth PASSED*",
        ]
    )

    # make sure that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_help_message(pytester):
    result = pytester.runpytest(
        "--help",
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(
        [
            "argus-server:",
            "*--argus-version=ARGUS_VERSION",
            "*Set the version of the Argus API server to run",
        ],
        consecutive=True,
    )


def test_argus_api_fixture(pytester):
    """Make sure that pytest accepts our fixture."""

    # create a temporary pytest test module
    pytester.makepyfile("""
        def test_sth(argus_api):
            url, token = argus_api
            assert url == "http://localhost:8000/api/v2"
    """)

    # run pytest with the following cmd args
    plugin_dir = os.path.dirname(pytest_argus_server.__file__)
    docker_compose_file = os.path.join(plugin_dir, "docker", "docker-compose.yml")
    result = pytester.runpytest(
        "--argus-version=1.30.0",  # Because 1.33 (latest) is broken
        f"--docker-compose={docker_compose_file}",
        "-v",
    )

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(
        [
            "*::test_sth PASSED*",
        ]
    )

    # make sure that we get a '0' exit code for the testsuite
    assert result.ret == 0
