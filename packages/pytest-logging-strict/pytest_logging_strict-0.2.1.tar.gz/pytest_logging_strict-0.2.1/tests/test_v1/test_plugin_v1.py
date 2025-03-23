"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Test module pytest_logging_strict.plugin_v1

.. code-block:: shell

   pytest --showlocals -vv tests/test_v1/test_plugin_v1.py

Check ``logging_strict`` fixture is recognized

.. code-block:: shell

   pytest --fixtures

In temp folder, 1st activate venv.

.. code-block:: shell

   pytest --showlocals -r a -vv tests/test_foobar.py::test_fcn

.. seealso::

   `logassert <https://pypi.org/project/logassert/>`_

"""

import warnings
from contextlib import nullcontext as does_not_raise
from pathlib import (
    Path,
    PurePath,
)
from unittest.mock import patch

import pytest

from pytest_logging_strict.plugin_v1 import (
    RegistryPackageNameStash,
    RegistryPathStash,
)

testdata_config_in_pyproject_toml = (
    (
        "awesomepackage",
        "0.0.1",
        "logging_strict",
        "configs",
        "worker",
        "mp",
        "asz",
        "1",
        "asz",
        None,
        """log this important message""",
    ),
    (
        "awesomepackage",
        "0.0.1",
        "coverage",
        "configs",
        "worker",
        "mp",
        "asz",
        "1",
        "asz",
        None,
        """log this important message""",
    ),
    (
        "awesomepackage",
        "0.0.1",
        "logging_strict",
        "configs",
        "worker",
        "mp",
        "asz",
        "1",
        "logging_strict",
        "Logger",
        """log this important message""",
    ),
    (
        "awesomepackage",
        "0.0.1",
        "logging_strict",
        "configs",
        "worker",
        "mp",
        "asz",
        "1",
        None,
        "Logger",
        """log this important message""",
    ),
    (
        "awesomepackage",
        "0.0.1",
        "logassert",
        "configs",
        "worker",
        "mp",
        "asz",
        "1",
        "logassert",
        None,
        """log this important message""",
    ),
)
ids_config_in_pyproject_toml = (
    "loggers.asz successful extract logging config YAML",
    "Unsuccessful search. Package data lacks logging config YAML files",
    "loggers.logging_strict",
    "get root logger",
    "logassert not installed in venv becomes ImportError",
)


@pytest.mark.parametrize(
    (
        "package_name, package_version, yaml_package_name, "
        "package_data_folder_start, category, genre, flavor, version_no, "
        "dotted_path_handler_package_name, expected_type, msg"
    ),
    testdata_config_in_pyproject_toml,
    ids=ids_config_in_pyproject_toml,
)
def test_fixture_logging_strict_v1(
    package_name,
    package_version,
    yaml_package_name,
    package_data_folder_start,
    category,
    genre,
    flavor,
    version_no,
    dotted_path_handler_package_name,
    expected_type,
    msg,
    pytester,
    impl_version_no,
    # xdist_args,
):
    """Test logging_strict plugin"""
    # pytest --showlocals -r a -vv --log-level INFO -k "test_fixture_logging_strict_v1" tests
    # prepare
    path_pytester = pytester.path  # noqa: F841
    #    pytest plugins (specified in ``conftest.py`` module variable, pytest_plugins)
    lst_plugins = pytester.plugins  # noqa: F841
    #    pyproject.toml
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
        f"""name = "{package_name}"\n"""
        f"""version = "{package_version}"\n\n"""
        """[tool.pytest.ini_options]\n"""
        f"""logging_strict_impl_version_no = "{impl_version_no}"\n"""
        f"""logging_strict_yaml_package_name = '{yaml_package_name}'\n"""
        f"""logging_strict_package_data_folder_start = '{package_data_folder_start}'\n"""
        f"""logging_strict_category = '{category}'\n"""
        f"""logging_strict_genre = '{genre}'\n"""
        f"""logging_strict_flavor = '{flavor}'\n"""
        f"""logging_strict_version_no = '{version_no}'\n"""
        "\n"
        "\n"
    )
    pytester.makepyprojecttoml(config_text)

    #    conftest.py
    path_src = Path(__file__).parent.parent.joinpath("conftest.py")
    conftest_text = path_src.read_text()
    pytester.makeconftest(conftest_text)

    #    a test file
    #    import logging_strict as ls
    name = "test_logging_strict_main_v1"
    test_text = (
        f"""
            import logging

            from logging_strict.tech_niques import captureLogs
            import pytest

            @pytest.mark.logging_package_name("{dotted_path_handler_package_name}" if "{dotted_path_handler_package_name}" != "None" else None)
            def test_fcn_logging_strict_main_v1(logging_strict):
                # fixture method should delay execution. So can control when
                # logging config YAML verification and logger initializing occurs
                t_two = logging_strict()
                if t_two is None:
                    # error occurred. Check warnings
                    assert '{expected_type!s}' == 'None'
                else:
                    assert isinstance(t_two, tuple)
                    t_two_len = len(t_two)
                    assert t_two_len == 2
                    logger, loggers = t_two

                    loggers_count = len(loggers)
                    assert loggers_count >= 3

                    # If pytest.mark.logging_package_name not provided, initializes root logger
                    # If pytest.mark.logging_package_name provided, initializes that logger
                    # If pytest.mark.logging_package_name provided but not in config loggers ... ??
                    pass

                    logger_name_actual = logger.name
                    logger_level_name_actual = logging.getLevelName(logger.level)

                    logger_name_expected = "{dotted_path_handler_package_name}"
                    if logger_name_expected == "None":
                        assert logger_name_actual == "root"
                        fcn = logger.error
                    else:
                        assert logger_name_actual == logger_name_expected
                        fcn = logger.info

                    # Show logger works
                    with captureLogs(
                        logger_name_actual,
                        level=logger_level_name_actual,
                    ) as cm:
                        fcn('{msg}')
                    out = cm.output
                    is_found = False
                    for msg_full in out:
                        if msg_full.endswith('{msg}'):
                            is_found = True
                    assert is_found

        """,
    )
    pytester.makepyfile(**{name: test_text})

    """
    import os
    path_covrc = pytester.path.joinpath(".coveragerc")
    path_cov = pytester.path.joinpath(".coverage_sub")
    coveragerc = (
        f"[run]{os.linesep}"
        f"data_file={str(path_cov)}{os.linesep}{os.linesep}"
    )
    if not path_covrc.exists():
        path_covrc.write_text(coveragerc)

    if os.environ.get("COVERAGE_PROCESS_START", None) is None:
        # normally should contain path to a .coveragerc file
        os.environ["COVERAGE_PROCESS_START"] = path_covrc.as_posix()
    """
    pass

    args = (
        "--showlocals",
        "-vv",
        "-k",
        "test_logging_strict_main_v1",
    )
    kwargs = {}
    run_result = pytester.runpytest_subprocess(*args, **kwargs)
    out = run_result.outlines  # noqa: F841
    err = run_result.errlines  # noqa: F841
    outcomes = run_result.parseoutcomes()  # noqa: F841
    exit_code = run_result.ret
    assert exit_code == 0


testdata_registry_package_path_stash = (
    (
        "deleteme.logging.config.yaml",
        str,
        does_not_raise(),
        "deleteme.logging.config.yaml",
    ),
    (
        "deleteme.logging.config.yaml",
        Path,
        does_not_raise(),
        "deleteme.logging.config.yaml",
    ),
    (
        0.2345,
        float,
        pytest.raises(TypeError),
        0.2345,
    ),
    (
        None,
        type(None),
        does_not_raise(),
        None,
    ),
)
ids_registry_package_path_stash = (
    "path",
    "Path",
    "float",
    "None",
)


@pytest.mark.parametrize(
    "relpath_f, datatype, expectation, relpath_expected",
    testdata_registry_package_path_stash,
    ids=ids_registry_package_path_stash,
)
def test_registry_package_path_stash(
    relpath_f,
    datatype,
    expectation,
    relpath_expected,
    tmp_path,
):
    """Serialized/deserialize a path"""
    # pytest --showlocals -r a -vv --log-level INFO -k "test_registry_package_path_stash" tests

    if datatype == str:
        abspath_f = tmp_path.joinpath(relpath_f)
        f_abspath = str(abspath_f)
    elif issubclass(datatype, PurePath):
        abspath_f = tmp_path.joinpath(relpath_f)
        f_abspath = abspath_f
    else:
        f_abspath = relpath_f

    with expectation:
        cs = RegistryPathStash.from_serialized(f_abspath)
    if isinstance(expectation, does_not_raise):
        f_abspath_actual = cs.serialized()
        if f_abspath_actual is None:
            assert f_abspath_actual is None
        else:
            abspath_f_actual = Path(f_abspath_actual)
            f_relpath_actual = str(abspath_f_actual.relative_to(tmp_path))
            f_relpath_expected = str(relpath_f)
            assert f_relpath_actual == f_relpath_expected


testdata_registry_package_name_stash = (
    (
        "logging-strict",
        does_not_raise(),
        "logging_strict",
    ),
    (
        "zope.interface",
        does_not_raise(),
        "zope.interface",
    ),
    (
        0.12345,
        does_not_raise(),
        None,
    ),
    (
        None,
        does_not_raise(),
        None,
    ),
    (
        "   ",
        does_not_raise(),
        None,
    ),
)
id_registry_package_name_stash = (
    "package name contains hyphen",
    "package name contains period",
    "unsupported type becomes None no exception",
    "None becomes None no exception",
    "whitespace becomes None no exception",
)


@pytest.mark.parametrize(
    "package_name, expectation, package_name_expected",
    testdata_registry_package_name_stash,
    ids=id_registry_package_name_stash,
)
def test_registry_package_name_stash(
    package_name,
    expectation,
    package_name_expected,
):
    """Test RegistryPackageNameStash"""
    # pytest --showlocals -r a -vv --log-level INFO -k "test_registry_package_name_stash" tests
    with expectation:
        rpn = RegistryPackageNameStash.from_serialized(package_name)
    if isinstance(expectation, does_not_raise):
        package_name_actual = rpn.serialized()
        assert package_name_actual == package_name_expected


testdata_configure = (
    (
        "write this to file",
        True,
    ),
    (
        "write this to file",
        False,
    ),
    (
        None,
        True,
    ),
)
ids_configure = (
    "str_yaml extracts a str xdist on",
    "str_yaml extracts a str xdist off",
    "str_yaml extraction fails None",
)


@pytest.mark.parametrize(
    "get_yaml_return_value, is_xdist_plugin_on",
    testdata_configure,
    ids=ids_configure,
)
def test_configure_v1(
    get_yaml_return_value,
    is_xdist_plugin_on,
    pytester: pytest.Pytester,
):
    """Test pytest_configure hook"""
    # pytest --showlocals -r a -vv --log-level INFO -k "test_configure_v1" tests
    from pytest_logging_strict.plugin_wireframe import pytest_configure as configure

    args = ()
    with warnings.catch_warnings(record=False):
        warnings.simplefilter(action="ignore", category=UserWarning)
        config = pytester.parseconfig(*args)

    path_pytester = pytester.path

    # with patch("pytest_logging_strict.plugin_v0._xdist_worker", return_value=False):
    # with patch("pytest.Config.pluginmanager.register", return_value=True):
    # with patch("pytest.Config.pluginmanager.getplugin", return_value=True):
    with patch(
        "pytest_logging_strict.plugin_v1.get_temp_folder",
        return_value=path_pytester,
    ):
        with patch(
            "pytest_logging_strict.plugin_v1.is_xdist",
            return_value=is_xdist_plugin_on,
        ):
            with warnings.catch_warnings(record=False):
                warnings.simplefilter(action="ignore", category=UserWarning)
                configure(config)
                """remove temp file tracked by pytest stash. Normally
                done by pytest_unconfigure"""
                # key = stash_key["config"]
                # stash_inst = config.stash[key]
                # stash_inst.remove()
                pass
