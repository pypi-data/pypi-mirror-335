"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

.. py:data:: stash_key
   :type: dict[str, pytest.StashKey[pytest_logging_strict.plugin_v1.RegistryPathStash]]

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
from contextlib import suppress
from dataclasses import dataclass
from pathlib import (
    Path,
    PurePath,
)

import pytest
import strictyaml as s
from logging_strict.logging_yaml_validate import validate_yaml_dirty
from logging_strict.register_config import (
    CONFIG_STEM,
    CONFIG_SUFFIX,
    ExtractorLoggingConfig,
)
from logging_strict.util.check_type import (
    is_not_ok,
    is_ok,
)

from .plugin_shared import item_marker
from .util import (
    get_qualname,
    get_query_v1,
    get_temp_folder,
    get_yaml_v1_extract,
)
from .util_xdist import (
    is_xdist,
    xdist_workerinput,
)


@dataclass(frozen=True)  # compat python < 3.10 (kw_only=True)
class RegistryPackageNameStash:
    """package containing the registry of logging strict YAML files

    .. py:attribute:: yaml_package_name
       :type: str | None

       Name of package with package data at base folder, ``logging_strict.yml``
       Need not be ``logging_strict``, but recommended to choose a curated package
       with is actively maintained.

    """

    yaml_package_name: str | None

    @classmethod
    def from_serialized(cls, serialized):
        """Factory / setter

        :py:func:`pytest_logging_strict.util.get_yaml_v1_extract` sets a fallback
        package name. The values provided by either config or cli, could
        still be an empty string or non-str. In which case, package name may
        be coersed to None.

        :param serialized:

           Raw package name. Chars might include hyphen underscore or period

        :type serialized: typing.Any | None
        """
        if is_ok(serialized):
            fcn = ExtractorLoggingConfig.clean_package_name
            yaml_package_name = fcn(serialized)
        else:
            # unsupported type or None or bunch of whitespace
            yaml_package_name = None

        return cls(yaml_package_name=yaml_package_name)

    def serialized(self):
        """Getter

        :returns: posix path to registry of logging strict config YAML files
        :rtype: str | None
        """
        ret = self.yaml_package_name

        return ret


@dataclass(frozen=True)  # compat python < 3.10 (kw_only=True)
class RegistryPathStash:
    """Plugin data stored in the pytest.Config stash.

    .. py:attribute:: registry_logging_strict_config_yaml_path
       :type: pathlib.Path | None

       Path to registry of logging config YAML files.
       None if either ``pyproject.toml [tool.pytest.ini_options]`` field
       ``logging_strict_yaml_package_name`` not set or package
       does not contain a ``logging_strict.yml`` file

    """

    registry_logging_strict_config_yaml_path: Path | None

    @classmethod
    def from_serialized(cls, serialized):
        """Factory / setter

        :param serialized: posix path to set into pytest stash
        :type serialized: str | pathlib.Path | None
        :returns: key used by pytest.stash
        :rtype: pytest_logging_strict.plugin_v1.RegistryPathStash
        :raises:

           - :py:exc:`TypeError` -- unsupported type expecting absolute
             path. Either Path or posix str or None

        """
        if serialized is None:
            path_f = None
        else:
            if isinstance(serialized, str) and len(serialized.strip()) != 0:
                path_f = Path(serialized)
            elif issubclass(type(serialized), PurePath):
                path_f = serialized
            else:
                msg_warn = f"unsupported type expecting Path or posix str got {type(serialized)}"
                raise TypeError(msg_warn)

        return cls(registry_logging_strict_config_yaml_path=path_f)

    def remove(self):
        """Attempt to unlink temp file.

        On Windows. The process cannot access the file because
        it is being used by another process
        """
        if self.registry_logging_strict_config_yaml_path is not None:
            with suppress(OSError):
                self.registry_logging_strict_config_yaml_path.unlink(missing_ok=True)
        else:  # pragma: no cover
            pass

    def serialized(self):
        """Getter

        :returns: posix path to registry of logging strict config YAML files
        :rtype: str | None
        """
        if self.registry_logging_strict_config_yaml_path is None:
            ret = None
        else:
            ret = str(self.registry_logging_strict_config_yaml_path)

        return ret


stash_key = {
    "package_name": pytest.StashKey[RegistryPackageNameStash](),
    "registry": pytest.StashKey[RegistryPathStash](),
}


class LoggingStrictXdistControllerPlugin:
    """pytest-xdist plugin that is only registered on xdist controller processes"""

    def pytest_configure_node(self, node):
        """Pass the config stash to workers.

        :param node: A worker instance
        :type node: xdist.workermanage.WorkerController
        """
        xdist_workerinput(node)["registry_logging_config_yaml_serialized"] = (
            node.config.stash[stash_key["registry"]].serialized()
        )
        xdist_workerinput(node)["registry_package_name_serialized"] = node.config.stash[
            stash_key["package_name"]
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
    key_registry = stash_key["registry"]
    key_package_name = stash_key["package_name"]

    if not xdist_worker_:
        config.pluginmanager.register(LoggingStrictControllerPlugin())

        """Extracts registry. Refrain from read and validate YAML file.
        File name is not randomized which is a security issue."""
        t_registry = get_yaml_v1_extract(
            config,
            path_alternative_dest_folder=get_temp_folder(),
        )
        package_name_fixed, path_registry = t_registry

        if package_name_fixed is None or path_registry is None:
            # Write warning
            msg_warn = (
                "Failed to extract registry of logging config YAML files. "
                "Either pyproject.toml section [tool.pytest.ini_options] "
                f"""field {get_qualname("yaml_package_name")} not set """
                "or package does not contain a "
                f"{CONFIG_STEM}{CONFIG_SUFFIX} file"
            )
            warnings.warn(msg_warn)
        else:
            pass
        config.stash[key_registry] = RegistryPathStash(
            registry_logging_strict_config_yaml_path=path_registry,
        )
        config.stash[key_package_name] = RegistryPackageNameStash(
            yaml_package_name=package_name_fixed,
        )
        # If xdist is enabled, then the results path should be exposed to
        # the workers so that they know where to read raw logging config YAML from.
        if is_xdist(config):
            config.pluginmanager.register(LoggingStrictXdistControllerPlugin())
        else:  # pragma: no cover
            pass
    else:
        # xdist workers create the stash using input from the controller plugin.
        config.stash[key_registry] = RegistryPathStash.from_serialized(
            xdist_worker_["input"]["registry_logging_config_yaml_serialized"]
        )
        config.stash[key_package_name] = RegistryPackageNameStash.from_serialized(
            xdist_worker_["input"]["registry_package_name_serialized"]
        )

    # https://docs.pytest.org/en/stable/how-to/writing_plugins.html#registering-custom-markers
    config.addinivalue_line(
        "markers",
        f"{item_marker}(arg): name of package containing logging config YAML files",
    )


class LoggingStrictControllerPlugin:
    """pytest plugin for logging-strict"""

    def pytest_unconfigure(self, config):
        """Clean up temp file tracked by pytest stash.

        :param config: pytest configuration
        :type config: pytest.Config
        """
        stash_inst = config.stash[stash_key["registry"]]
        stash_inst.remove()


@pytest.fixture(scope="session")
def registry_get_stash_path(request: pytest.FixtureRequest):
    """From pytest stash, get path to registry of logging config YAML.
    File contains not validated YAML str.

    :returns: Path to registry of logging config YAML or None.
    :rtype: pathlib.Path | None
    """
    key = stash_key["registry"]
    dc_stash = request.config.stash[key]

    ls_yaml_f_path = dc_stash.serialized()

    if ls_yaml_f_path is None:
        return None
    else:
        ret = Path(ls_yaml_f_path)

    return ret


@pytest.fixture(scope="session")
def registry_get(registry_get_stash_path: pytest.Fixture):
    """From pytest stash, get path to tempfile. Contains
    logging config YAML str.

    :returns: logging config YAML str
    :rtype: tuple[str | None, pathlib.Path | None]
    """
    path_registry_yaml_f = registry_get_stash_path
    msg_warn = (
        "Could not read extracted registry of logging config YAML from "
        f"temp file {path_registry_yaml_f!r}"
    )
    if path_registry_yaml_f is None:
        warnings.warn(msg_warn)
        str_yaml_raw = None
    else:
        try:
            # When extracted, written as text not bytes
            str_yaml_raw = path_registry_yaml_f.read_text()
        except (OSError, Exception) as exc:
            # catch-all Exception not expected
            msg_warn_2 = f"{msg_warn} {exc!r}"
            warnings.warn(msg_warn_2)
            str_yaml_raw = None

    t_ret = (str_yaml_raw, path_registry_yaml_f)

    return t_ret


@pytest.fixture(scope="session")
def registry_validate(request: pytest.FixtureRequest, registry_get: pytest.Fixture):
    """Validate registry of logging strict YAML files

    :returns: instance of ExtractorLoggingConfig on success otherwise None
    :rtype: logging_strict.register_config.ExtractorLoggingConfig | None
    :raises:

       - :py:exc:`strictyaml.YAMLValidationError` -- validation failed

    """
    # ExtractorLoggingConfig needs package name
    key_package_name = stash_key["package_name"]
    dc_stash = request.config.stash[key_package_name]
    package_name = dc_stash.serialized()

    is_package_name_ng = package_name is None
    if is_package_name_ng:
        msg_warn = (
            "In pyproject.toml [tool.pytest.ini_options], missing field "
            f"""{get_qualname("yaml_package_name")} or retrieving from stash failed"""
        )
        warnings.warn(msg_warn)
        ret = None
    else:
        t_two = registry_get
        str_yaml_raw, path_registry_yaml_f = t_two

        is_extract_fail = path_registry_yaml_f is None or is_not_ok(str_yaml_raw)
        if is_extract_fail:
            msg_warn = (
                "Extraction of registry of logging strict YAML config "
                "unsuccessful. Nothing to validate"
            )
            warnings.warn(msg_warn)
            ret = None
        else:
            path_alternative_dest_folder = path_registry_yaml_f.parent
            elc = ExtractorLoggingConfig(
                package_name,
                path_alternative_dest_folder=path_alternative_dest_folder,
            )
            # May raise strictyaml.YAMLValidationError
            elc.get_db(path_extracted_db=path_registry_yaml_f)
            ret = elc

    return ret


@pytest.fixture
def get_d_config_initialize():
    """Initialize the logging config dict.

    To understand what the logging configuration did, returns a ``list[loggers]``

    logger has yet to be initialize.

    :returns: None if some failure otherwise list of loggers
    :rtype: list[logging.Logger] | None
    """

    def _method(d_config):
        """Return available ``list[logging.Logger]``"""
        import logging
        import logging.config

        # d_config = get_d_config()
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
    registry_validate: pytest.Fixture,
    get_d_config_initialize: pytest.Fixture,
    caplog: pytest.LogCaptureFixture,
):
    """Logging configuration, stored as package data.
    Gets extracted once, validated, applied to each test item

    Usage

    .. code-block:: text

       @pytest.mark.logging_package_name("wreck")
       def test_test_something(logging_strict):
           t_loggers = logging_strict
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

        # May raise strictyaml.YAMLValidationError
        try:
            elc = registry_validate
        except s.YAMLValidationError:
            msg_warn = (
                "registry of logging strict config YAML files. YAML validation failed"
            )
            warnings.warn(msg_warn)
            elc is None

        if elc is None:
            # an error occurred check warnings
            ret = None
        else:
            # get query. Skips setup
            d_query = get_query_v1(request.config)
            elc.query_db(
                d_query["category"],
                genre=d_query["genre"],
                flavor=d_query["flavor"],
                version_no=d_query["version_no"],
                logger_package_name=logging_package_name,
            )
            #    A successful query, validation occurred
            # lc_yaml_relpath = elc.logging_config_yaml_relpath
            lc_yaml_str = elc.logging_config_yaml_str

            if lc_yaml_str is not None:
                yaml_config = validate_yaml_dirty(lc_yaml_str)
                d_config = yaml_config.data
                lst_loggers = get_d_config_initialize(d_config)

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
            else:
                ret = None

        return ret

    return _method
