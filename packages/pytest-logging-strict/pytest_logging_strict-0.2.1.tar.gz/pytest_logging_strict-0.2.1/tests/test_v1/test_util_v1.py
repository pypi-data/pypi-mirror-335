"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Test utils introduced in impl_version_no 1

"""

import warnings
from unittest.mock import patch

import pytest

from pytest_logging_strict.util import (
    get_query_v1,
    get_yaml_v1_extract,
)

testdata_get_query_v1 = (
    (
        """logging_strict_impl_version_no = "1"\n"""
        """logging_strict_yaml_package_name = 'logging-strict'\n"""
        """logging_strict_category = 'worker'\n"""
        """logging_strict_genre = 'mp'\n"""
        """logging_strict_flavor = 'asz'\n"""
        """logging_strict_version_no = '1'\n"""
    ),
    (
        """logging_strict_yaml_package_name = 'logging-strict'\n"""
        """logging_strict_category = 'worker'\n"""
        """logging_strict_genre = 'mp'\n"""
        """logging_strict_flavor = 'asz'\n"""
        """logging_strict_version_no = '1'\n"""
    ),
)
ids_get_query_v1 = (
    "with impl_version_no provided",
    "without impl_version_no",
)


@pytest.mark.parametrize(
    "query",
    testdata_get_query_v1,
    ids=ids_get_query_v1,
)
def test_get_query_v1(
    query,
    pytester,
):
    """Test converting config into a v1 query"""
    # pytest --showlocals -r a -vv --log-level INFO -k "test_get_query_v1" tests
    config_text = (
        "[build-system]\n"
        "requires = [\n"
        """    "setuptools>=70.0.0",\n"""
        """    "wheel",\n"""
        """    "build",\n"""
        """    "setuptools_scm>=8",\n"""
        "]\n"
        'build-backend = "setuptools.build_meta"\n\n'
        "[project]\n"
        """name = "whatever"\n"""
        """version = "0.0.1"\n\n"""
        """[tool.pytest.ini_options]\n"""
        f"{query}"
        "\n"
        "\n"
    )
    pytester.makepyprojecttoml(config_text)

    args = ()
    with warnings.catch_warnings(record=False):
        warnings.simplefilter(action="ignore", category=UserWarning)
        config = pytester.parseconfig(*args)

    d_config = get_query_v1(config)
    assert isinstance(d_config, dict)


def test_get_yaml_v1_extract(
    pytester,
):
    """Test get_yaml_v1_extract"""
    # pytest --showlocals -r a -vv --log-level INFO -k "test_get_yaml_v1_extract" tests
    # prepare
    config_text = (
        "[build-system]\n"
        "requires = [\n"
        """    "setuptools>=70.0.0",\n"""
        """    "wheel",\n"""
        """    "build",\n"""
        """    "setuptools_scm>=8",\n"""
        "]\n"
        'build-backend = "setuptools.build_meta"\n\n'
        "[project]\n"
        """name = "whatever"\n"""
        """version = "0.0.1"\n\n"""
        """[tool.pytest.ini_options]\n"""
        """logging_strict_yaml_package_name = '  '\n"""
        "\n"
        "\n"
    )
    pytester.makepyprojecttoml(config_text)

    args = ()
    with warnings.catch_warnings(record=False):
        warnings.simplefilter(action="ignore", category=UserWarning)
        config = pytester.parseconfig(*args)

    with patch(
        "pytest_logging_strict.util._get_arg_value",
        return_value="",
    ):
        t_actual = get_yaml_v1_extract(config)
        assert isinstance(t_actual, tuple)
        assert t_actual[0] is None
        assert t_actual[1] is None

    # Need to cause ImportError by pretending logging_strict is not installed
    # https://stackoverflow.com/a/62456280
    # solution introduces a man in the middle class which implements find_spec.
    # reloads package logging_strict which would interfere with coverage
    pass
