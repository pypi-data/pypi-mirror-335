"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

.. py:data:: stash_key
   :type: dict[str, pytest.StashKey[pytest_logging_strict.plugin_v0.LSConfigStash]]

   Holds path to raw logging config YAML file.

.. seealso::

   General pytest plugin reference links

   `pytest.stash <https://docs.pytest.org/en/stable/_modules/_pytest/stash.html>`_

   `pytest reference <https://docs.pytest.org/en/stable/reference/reference.html>`_

   pytest plugin storing data links

   `storing data and across-hook-functions <https://docs.pytest.org/en/stable/how-to/writing_hook_functions.html#storing-data-on-items-across-hook-functions>`_

   `pytest plugin reporting <https://stackoverflow.com/questions/76116140/pytest-how-to-attach-runtime-info-to-test-item-for-reporting>`_

   Storing data with a pytest plugin

   ``pytest-mypy`` guided how to go about writing a modern pytest plugin.
   Huge credit to the ``pytest-mypy`` team and contributors. Without
   which the results would have been less robust.

   `[repo] <https://github.com/realpython/pytest-mypy>`_
   `[source] <https://github.com/realpython/pytest-mypy/blob/main/src/pytest_mypy/__init__.py>`_

Notable other plugins

"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import (
    Path,
    PurePath,
)
from tempfile import NamedTemporaryFile

import pytest
import strictyaml as s
from logging_strict.logging_yaml_abc import after_as_str_update_package_name
from logging_strict.logging_yaml_validate import validate_yaml_dirty

from .plugin_shared import item_marker
from .util import get_yaml_v0
from .util_xdist import (
    is_xdist,
    xdist_workerinput,
)


@dataclass(frozen=True)  # compat python < 3.10 (kw_only=True)
class LSConfigStash:
    """Plugin data stored in the pytest.Config stash.

    :ivar logging_strict_config_yaml_path:

       From a package containing logging-strict config YAML files,
       destination path of an extracted file.

    :vartype: pathlib.Path
    """

    logging_strict_config_yaml_path: Path

    @classmethod
    def from_serialized(cls, serialized):
        """Factory / setter

        :param serialized: posix path to set into pytest stash
        :type serialized: str | pathlib.Path
        :returns: key used by pytest.stash
        :rtype: pytest_logging_strict.plugin_v0.LSConfigStash
        :raises:

           - :py:exc:`TypeError` -- unsupported type expecting absolute
             path. Either Path or posix str

        """
        is_str_ok = (
            serialized is not None
            and isinstance(serialized, str)
            and len(serialized.strip()) != 0
        )
        is_path_ok = serialized is not None and issubclass(type(serialized), PurePath)
        if is_str_ok:
            path_f = Path(serialized)
        elif is_path_ok:
            path_f = serialized
        else:
            msg_warn = (
                f"unsupported type expecting Path or posix str got {type(serialized)}"
            )
            raise TypeError(msg_warn)

        return cls(logging_strict_config_yaml_path=path_f)

    def remove(self):
        """Attempt to unlink temp file"""
        try:
            self.logging_strict_config_yaml_path.unlink(missing_ok=True)
        except OSError:
            """On Windows. The process cannot access the file because
            it is being used by another process"""
            pass

    def serialized(self):
        """Getter

        :returns: posix path to logging strict config YAML file
        :rtype: str
        """
        return str(self.logging_strict_config_yaml_path)


stash_key = {
    "config": pytest.StashKey[LSConfigStash](),
}


class LoggingStrictv0XdistControllerPlugin:
    """pytest-xdist plugin that is only registered on xdist controller processes"""

    def pytest_configure_node(self, node):
        """Pass the config stash to workers.

        :param node: A worker instance
        :type node: xdist.workermanage.WorkerController
        """
        xdist_workerinput(node)["logging_config_yaml_serialized"] = node.config.stash[
            stash_key["config"]
        ].serialized()


def _configure(config, xdist_worker_):
    """Initialize the path used to cache raw logging config YAML.

    Configure the plugin based on the CLI.

    :py:mod:`tempfile` does not automatically flush. Contents in a buffer
    upon close writes buffer to file.

    pypy correctly doesn't see contents in file cuz its in buffer until
    the file is closed. Rather than wait for a close, flush the buffer
    to file.

    >>> from pathlib import Path
    >>> from tempfile import NamedTemporaryFile
    >>> f = NamedTemporaryFile(delete=False)
    >>> f.write(b"Hello World!")
    12
    >>> Path(f.name).stat().st_size
    0
    >>> f.flush()
    >>> Path(f.name).stat().st_size
    12

    :param config: pytest configuration
    :type config: pytest.Config
    :param xdist_worker_: pytest config passed to worker
    :type xdist_worker_: dict[str, xdist.workermanage.WorkerController | pytest.Config]

    .. todo:: Change base folder

       Runner is pytest, not :py:class:`tempfile.NamedTemporaryFile`.
       NamedTemporaryFile base folder is ``/tmp``. Should the base
       folder be in a pytest determined location?

    """
    key = stash_key["config"]
    if not xdist_worker_:
        config.pluginmanager.register(LoggingStrictv0ControllerPlugin())

        """
        import os
        env_cov = os.environ.get("COVERAGE_PROCESS_START", None)
        if env_cov is not None and isinstance(env_cov, str) and len(env_cov) != 0:
            import coverage

            coverage.process_startup()
        else:  # pragma: no cover
            pass
        """
        pass

        """tempfile.NamedTemporaryFile temp folder is ``/tmp``.
        Instead use _pytest.tmpdir.TempPathFactory.getbasetemp which is
        similar to session scoped

        given_basetemp = None
        retention_count = 0
        temppath_factory = pytest.TempPathFactory(
            given_basetemp,
            retention_count,
            retention_policy="all",
            trace=config.trace.get("tmpdir"),
        )
        path_dir = temppath_factory.mktemp("session-", numbered=True)
        # Get the path to a temporary file
        f = NamedTemporaryFile(delete=False, dir=path_dir)
        """
        f = NamedTemporaryFile(delete=False)
        path_f = Path(f.name)

        """Search for logging config YAML file. Validate then write
        contents to buffer then flush to temp file"""
        str_yaml = get_yaml_v0(config, path_f)
        if str_yaml is not None:
            bytes_yaml = str_yaml.encode("utf-8")
            f.write(bytes_yaml)
            f.flush()
        else:
            # Write warning
            msg_warn = (
                f"Failed to extract logging config YAML file to {path_f!r}. "
                f"check config options {config!r}"
            )
            warnings.warn(msg_warn)

        config.stash[key] = LSConfigStash(
            logging_strict_config_yaml_path=path_f,
        )

        # If xdist is enabled, then the results path should be exposed to
        # the workers so that they know where to read raw logging config YAML from.
        if is_xdist(config):
            config.pluginmanager.register(LoggingStrictv0XdistControllerPlugin())
        else:  # pragma: no cover
            pass
    else:
        # xdist workers create the stash using input from the controller plugin.
        config.stash[key] = LSConfigStash.from_serialized(
            xdist_worker_["input"]["logging_config_yaml_serialized"]
        )

    # https://docs.pytest.org/en/stable/how-to/writing_plugins.html#registering-custom-markers
    config.addinivalue_line(
        "markers",
        f"{item_marker}(arg): name of package containing logging config YAML files",
    )


class LoggingStrictv0ControllerPlugin:
    """pytest plugin for logging-strict"""

    def pytest_unconfigure(self, config):
        """Clean up temp file tracked by pytest stash.

        :param config: pytest configuration
        :type config: pytest.Config
        """
        stash_inst = config.stash[stash_key["config"]]
        stash_inst.remove()


@pytest.fixture(scope="session")
def logging_strict_get_stash_path(request: pytest.FixtureRequest):
    """From pytest stash, get path to tempfile. Contains
    logging config YAML str.

    :returns: temp file Path. File should contain logging config YAML str
    :rtype: pathlib.Path
    """
    key = stash_key["config"]
    dc_stash = request.config.stash[key]
    ls_yaml_f_path = dc_stash.serialized()

    # read contents of logging config YAML file
    path_ls_yaml_f = Path(ls_yaml_f_path)
    return path_ls_yaml_f


@pytest.fixture(scope="session")
def logging_strict_get(logging_strict_get_stash_path: pytest.Fixture):
    """From pytest stash, get path to tempfile. Contains
    logging config YAML str.

    :returns: logging config YAML str
    :rtype: tuple[str | None, pathlib.Path]
    """
    path_ls_yaml_f = logging_strict_get_stash_path

    try:
        bytes_yaml_raw = path_ls_yaml_f.read_bytes()
        str_yaml_raw = bytes_yaml_raw.decode()
    except (OSError, Exception) as exc:
        # catch-all Exception not expected
        msg_warn = (
            "Could not read extracted logging config YAML from "
            f"temp file {path_ls_yaml_f!r} {exc!r}"
        )
        warnings.warn(msg_warn)
        str_yaml_raw = None

    return (str_yaml_raw, path_ls_yaml_f)


@pytest.fixture
def get_d_config(
    request: pytest.FixtureRequest,
    logging_strict_get: pytest.Fixture,
):
    """Validate and get the logging configuration as a dict

    :returns: Valid logging configuration dict
    :rtype: dict[str, typing.Any] | None
    """

    def _method():
        """In the already extracted logging config YAML file,

        - get package name from the pytest marker
        - replaces package_name token with current package name
        - revalidates the logging config YAML str
        - returns config dict consumable by Python logging module

        issues warnings

        - if no logging config YAML file found

        - if validation of logging config YAML file fails

        """
        marker = request.node.get_closest_marker(item_marker)
        if marker is not None and len(marker.args) == 1:
            """Get fixture marker value.
            Should be a package name (alphanumeric and underscores)"""
            logging_package_name = marker.args[0]
        else:
            # want root logger
            logging_package_name = None

        # Get path, to logging config YAML file, from pytest stash
        t_two = logging_strict_get
        str_yaml_raw, path_f = t_two
        is_search_fail = (
            str_yaml_raw is None
            or not isinstance(str_yaml_raw, str)
            or (isinstance(str_yaml_raw, str) and len(str_yaml_raw.strip()) == 0)
        )
        if is_search_fail:  # pragma: no cover
            msg_warn = (
                "Search for a matching logging config YAML file failed. "
                f"Extracted temp file size: {path_f.stat().st_size} {path_f!r}"
                "Either package lacks these files or need to widen the "
                "search (parameters)"
            )
            warnings.warn(msg_warn)
            ret = None
        else:
            try:
                if logging_package_name is not None:
                    str_yaml = after_as_str_update_package_name(
                        str_yaml_raw,
                        logger_package_name=logging_package_name,
                    )
                else:  # pragma: no cover
                    """root and secondary loggers, but no primary.
                    Still token, package_name"""
                    str_yaml = str_yaml_raw
                yaml_config = validate_yaml_dirty(str_yaml)
                d_config = yaml_config.data
            except s.YAMLValidationError as exc:
                msg_warn = (
                    "Strict validation of logging config YAML failed. "
                    "Ignore loggers.package_name. It is a token that gets replaced. "
                    f"{str_yaml_raw} {exc!r}"
                )
                warnings.warn(msg_warn)
                ret = None
            else:
                ret = d_config

        return ret

    return _method


@pytest.fixture
def get_d_config_initialize(
    get_d_config: pytest.Fixture,
):
    """Initialize the logging config dict.

    To understand what the logging configuration did, returns a ``list[loggers]``

    logger has yet to be initialize.

    :returns: None if some failure otherwise list of loggers
    :rtype: list[logging.Logger] | None
    """

    def _method():
        """Return available ``list[logging.Logger]``"""
        import logging
        import logging.config

        d_config = get_d_config()
        if d_config is None:
            ret = None
        else:
            logging.config.dictConfig(d_config)

            # hardened against missing root logger
            loggers = [logging.getLogger()]  # get the root logger
            loggers = loggers + [
                logging.getLogger(name) for name in logging.root.manager.loggerDict
            ]
            ret = loggers

        return ret

    return _method


@pytest.fixture
def logging_strict(
    request: pytest.FixtureRequest,
    get_d_config_initialize: pytest.Fixture,
    caplog: pytest.LogCaptureFixture,
):
    """Logging configuration, stored as package data.
    Gets extracted once, validated, applied to each test item

    Usage

    .. code-block:: text

       @pytest.mark.logging_package_name("wreck")
       def test_test_something(logging_strict):
           if t_loggers is not None:
               logger, lst_loggers = t_loggers
           logger.info("Hello World!")

    logging_package_name -- dotted path or package name. logging handler id

    .. seealso::

       https://github.com/pytest-dev/pytest/issues/2270#issuecomment-292004699

       `use marker to pass data to fixture <https://docs.pytest.org/en/stable/how-to/fixtures.html#using-markers-to-pass-data-to-fixtures>`_

       `pytest.Function <https://docs.pytest.org/en/stable/reference/reference.html#function>`_

    """

    def _method():
        """A method delays execution so warnings can be captured

        :returns:

           None on unsuccessful search and extraction of a logging config
           YAML file otherwise a logger instance and list of loggers

        :rtype: tuple[logging.Logger, list[logging.Logger]] | None
        """
        marker = request.node.get_closest_marker(item_marker)
        if marker is not None and len(marker.args) == 1:
            """Get fixture marker value.
            Should be a package name (alphanumeric and underscores)"""
            logging_package_name = marker.args[0]
        else:
            # want root logger
            logging_package_name = None

        lst_loggers = get_d_config_initialize()

        if lst_loggers is None:
            # an error occurred check warnings
            ret = None
        else:
            import logging

            if logging_package_name is None:
                # get root logger
                logger = logging.getLogger(name=None)
            else:
                # d_config["loggers"][logging_package_name]["propagate"] = True
                logger = logging.getLogger(name=logging_package_name)

            logger.addHandler(hdlr=caplog.handler)
            caplog.handler.level = logger.level
            ret = (logger, lst_loggers)

        return ret

    return _method
