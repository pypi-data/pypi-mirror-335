"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Test module pytest_logging_strict.util

.. code-block:: shell

   pytest --showlocals -vv tests/test_v0/test_util_v0.py

"""

import warnings
from fnmatch import fnmatch
from pathlib import Path

import pytest

from pytest_logging_strict.util import (
    _parse_option_value,
    get_optname,
    get_qualname,
    get_yaml_v0,
)

testdata_get_yaml_v0 = (
    (
        "logging_strict",
        "configs",
        "worker",
        "mp",
        "asz",
        "1",
        str,
        None,
    ),
    (
        "",
        "configs",
        "worker",
        "mp",
        "asz",
        "1",
        str,
        None,
    ),
    (
        "logging_strict",
        "",
        "worker",
        "mp",
        "asz",
        "1",
        str,
        None,
    ),
    (
        "logassert",
        "configs",
        "worker",
        "mp",
        "asz",
        "1",
        None,
        "package_name * not installed. Before extracting package data, install the package into venv",
    ),
    (
        "logging_strict",
        "configs",
        "worker",
        "mp",
        "bob",
        "1",
        None,
        (
            "Within package *, starting from *, found *. Expected one. "
            "Is in this package? Is folder too specific? Try casting a wider net?"
        ),
    ),
    (
        "logging_strict",
        "bad_idea",
        "worker",
        "mp",
        "shared",
        "1",
        None,
        (
            "Within package *, starting from *, found *. Expected one. "
            "Adjust / narrow param, path_relative_package_dir"
        ),
    ),
    (
        "logging-strict",
        "configs",
        "worker",
        "mp",
        "asz",
        "1",
        str,
        None,
    ),
)
ids_get_yaml_v0 = (
    "successful query",
    "Has sane default for package name",
    "Has sane default for package_start_folder_name",
    "ImportError",
    "FileNotFoundError",
    "AssertionError",
    "extract issue",
)


@pytest.mark.parametrize(
    (
        "yaml_package_name, package_data_folder_start, category, genre, "
        "flavor, version_no, return_type, warning_msg"
    ),
    testdata_get_yaml_v0,
    ids=ids_get_yaml_v0,
)
def test_get_yaml_v0(
    yaml_package_name,
    package_data_folder_start,
    category,
    genre,
    flavor,
    version_no,
    return_type,
    warning_msg,
    pytester: pytest.Pytester,
    impl_version_no,
):
    """Call pytest_addoption to test util module"""
    # pytest --showlocals -r a -vv --log-level INFO -k "test_get_yaml_v0" tests
    path_pytester = pytester.path  # noqa: F841
    # prepare
    #    conftest.py
    path_src = Path(__file__).parent.parent.joinpath("conftest.py")
    conftest_text = path_src.read_text()
    pytester.makeconftest(conftest_text)

    #    cli options
    args = [
        get_optname("impl_version_no"),
        impl_version_no,
        get_optname("yaml_package_name"),
        yaml_package_name,
        get_optname("package_data_folder_start"),
        package_data_folder_start,
        get_optname("category"),
        category,
        get_optname("genre"),
        genre,
        get_optname("flavor"),
        flavor,
        get_optname("version_no"),
        version_no,
    ]
    # Calls pytest_cmdline_parse which calls pytest_addoption
    # ns = conf.option
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter(action="ignore", category=UserWarning)
        conf = pytester.parseconfig(*args)
        val = conf.getoption(get_qualname("yaml_package_name"))
    parsed_val = _parse_option_value(val)
    parsed_val_expected = _parse_option_value(yaml_package_name)
    assert parsed_val == parsed_val_expected

    # No configuration file prepared
    # assert conf.getini(get_qualname("yaml_package_name")) == yaml_package_name
    pass

    # from path_f gets path_pytester folder
    path_f = path_pytester.joinpath("deleteme.logging.config.yaml")

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter(action="ignore", category=UserWarning)
        out_actual = get_yaml_v0(conf, path_f)
        if len(w) == 1:
            assert issubclass(w[-1].category, UserWarning)
            msg_actual = str(w[-1].message)
            is_match = fnmatch(msg_actual, warning_msg)
            assert is_match

    if return_type is None:
        assert out_actual is None
    elif return_type is str:
        assert isinstance(out_actual, return_type)
    else:  # pragma: no cover
        pass
