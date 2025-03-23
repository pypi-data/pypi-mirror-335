"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

As much as possible, into a separate module, separate out imports to logging_strict.

.. py:data:: __all__
   :type: tuple[str, str, str, str]
   :value: ("get_query_v1", "get_temp_folder", "get_yaml_v0", "update_parser",)

   Module exports

.. py:data:: IMPLEMENTATION_VERSION_NO_DEFAULT
   :type: str
   :value: "1"

   Fallback plugin implementation version no

"""

from __future__ import annotations

import tempfile
import warnings
from collections.abc import Sequence
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
import strictyaml as s
from logging_strict.constants import LoggingConfigCategory
from logging_strict.logging_api import LoggingConfigYaml
from logging_strict.logging_yaml_abc import as_str
from logging_strict.util.check_type import is_not_ok

__all__ = (
    "get_query_v1",
    "get_temp_folder",
    "get_yaml_v0",
    "update_parser",
)

APP_NAME_TOKEN = "logging_strict"
CLI_NAME_TOKEN = "logging-strict"
IMPLEMENTATION_VERSION_NO_DEFAULT = "1"
IMPLEMENTATION_PACKAGE_NAME = APP_NAME_TOKEN


def _is_xdist(config):
    """Check whether xdist plugin is enabled

    :param config: pytest configuration
    :type config: pytest.Config
    :returns: The plugin registered under the given name otherwise None
    :rtype: typing.Any | None

    .. seealso::

       `pluggy.PluginManager.get_plugin <https://pluggy.readthedocs.io/en/stable/api_reference.html#pluggy.PluginManager.get_plugin>`_

    """
    ret = config.pluginmanager.getplugin("xdist")

    return ret


def get_qualname(name):
    """Get configuration option name

    :param name: configuration option name without the preceding token
    :type name: str
    :returns: fully qualified configuration option name
    :rtype: str
    """
    return f"{APP_NAME_TOKEN}_{name}"


def get_optname(name):
    """Get cli option name

    :param name: cli option name without the preceding token
    :type name: str
    :returns: fully qualified cli option name
    :rtype: str
    """
    return f"--{CLI_NAME_TOKEN}-{name.replace('_', '-')}"


def _add_option(
    parser: pytest.Parser,
    group: pytest.OptionGroup,
    *,
    name,
    help_text,
    default=None,
    required=True,
    choices=None,
) -> None:
    """Add ini and cli options

    So cli can override ini, apply default value only to ini

    :param parser: pytest cli parser
    :type parser: pytest.Parser
    :param group:

       parser option group. Options will have own section in :code:`pytest --help`

    :type group: pytest.OptionGroup
    :param name: Option name containing only alphanumeric and underscores
    :type name: str
    :param help_text: help description for the cli option
    :type help_text: str
    :param default:

       Default None. Default value of the cli and corresponding ini
       option. data type limited to str

    :type default: str | None
    :param required:

       Default True. If not True option is not required otherwise option is required

    :type required: bool | None
    :param choices: Default None. Selection of all known acceptable values
    :type choices: collections.abc.Sequence[str] | None
    """
    is_ng_required = required is None or not isinstance(required, bool)
    if is_ng_required:
        is_required = True
    else:
        is_required = required

    is_not_str = default is not None and not isinstance(default, str)
    if is_not_str:
        optstr_default = None
    else:
        optstr_default = default

    # All underscores
    qualname = get_qualname(name)

    """**default is applied only to ini**

    type=str,
    metavar=name.upper(),
    """
    kwargs = {
        "dest": qualname,
        "help": help_text,
        "required": is_required,
    }
    is_seq_choices = (
        choices is not None
        and isinstance(choices, Sequence)
        and not isinstance(choices, str)
    )
    if is_seq_choices:
        kwargs["choices"] = choices
    else:  # pragma: no cover
        pass

    """**default is applied only to ini**

    type="string",
    Retrieve using :code:`config.getini(name)`
    """
    parser.addini(qualname, default=optstr_default, help=help_text)
    group.addoption(
        get_optname(name),
        **kwargs,
    )


def update_parser(parser: pytest.Parser):
    """The config options are search filters. To aid in finding a raw
    logging strict config YAML. The logging configuration is then always known,
    strictly validated against a schema, DRY, and hopefully UX intuitive.

    - which package to configure logging for.
    - choose logging config YAML

    :param parser: pytest argparse parser
    :type parser: pytest.Parser
    """
    target_file_desc = "logging config YAML file"

    help_plugin_impl_version_no = (
        "Per package there can only be one pytest plugin. Choose the plugin "
        "implementation. Mature implementations can be keep around and "
        "gradually phased out"
    )

    help_package_name = f"name of the package containing {target_file_desc}"
    help_package_data_folder_start = (
        "Package base data folder name. Packages may customize. Does "
        "not assume folder is 'data'. Plugin implementation v0 only"
    )
    help_category = "Narrow down the search. Filter by process purpose"
    help_genre = (
        "Genre. If UI framework, examples: textual, rich. "
        "For worker, e.g. mp (meaning multiprocessing). Preferably one "
        "word w/o hyphen periods or underscores"
    )
    help_flavor = (
        "Flavor (or name). Specific logging config serving a particular purpose. "
        "Preferably one word w/o hyphen periods or underscores"
    )
    help_version_no = (
        f"{target_file_desc} version. Flavor is optional, so applies "
        "to either: genre only or genre/flavor. Not to be confused with: yaml "
        "spec or logging.config version"
    )
    # default_package_data_folder_start = "configs"
    default_category = LoggingConfigCategory.UI.value

    group = parser.getgroup(CLI_NAME_TOKEN)

    _add_option(
        parser,
        group,
        name="impl_version_no",
        help_text=help_plugin_impl_version_no,
        default=IMPLEMENTATION_VERSION_NO_DEFAULT,
        required=False,
        choices=["0", "1"],
    )
    _add_option(
        parser,
        group,
        name="yaml_package_name",
        help_text=help_package_name,
        default=None,
        required=False,
    )
    _add_option(
        parser,
        group,
        name="package_data_folder_start",
        help_text=help_package_data_folder_start,
        default=None,
        required=False,
    )

    # choices = ["worker", "app"]. Controls choice of setup function
    _add_option(
        parser,
        group,
        name="category",
        help_text=help_category,
        default=default_category,
        required=False,
        choices=list(LoggingConfigCategory.categories()),
    )
    _add_option(
        parser,
        group,
        name="genre",
        help_text=help_genre,
        required=False,
    )
    _add_option(
        parser,
        group,
        name="flavor",
        help_text=help_flavor,
        required=False,
    )
    _add_option(
        parser,
        group,
        name="version_no",
        help_text=help_version_no,
        required=False,
    )


def _get_fallback_category() -> str:
    """With no configuration provided in pyproject.toml, there must be
    a sane default. Get sane default for category

    :returns: fallback for category
    :rtype: str
    """
    ret = LoggingConfigCategory.WORKER.value

    return ret


def _get_fallback_package_data_folder_start() -> str:
    """With no configuration provided in pyproject.toml, there must be
    a sane default. Get sane default for package_data_folder_start

    :returns: fallback for package_data_folder_start
    :rtype: str
    """
    ret = "configs"

    return ret


def _get_fallback_package_name() -> str:
    """With no configuration provided in pyproject.toml, there must be
    a sane default. Get sane default for package name

    :returns: fallback for package_name
    :rtype: str
    """
    ret = APP_NAME_TOKEN

    return ret


def get_yaml_v1_extract(conf, path_alternative_dest_folder=None):
    """Retrieve registry db YAML file.

    Save into stash.

    :param conf: pytest configuration class instance
    :type conf: pytest.Config
    :param path_alternative_dest_folder: absolute path to destination folder
    :type path_alternative_dest_folder: pathlib.Path | None
    :returns: package name and path to Registry of logging config YAML files
    :rtype: tuple[str | None, Pathlib.Path | None]
    """
    try:
        # logging-strict>=1.4.2
        from logging_strict.register_config import ExtractorLoggingConfig
    except ImportError:
        raise

    # requirements -- extract registry db
    name = get_qualname("yaml_package_name")
    package_name = _get_arg_value(conf, name, _get_fallback_package_name())

    # :code:`is_test_file=False` -- retrieving db, not the logging config YAML file
    if is_not_ok(package_name):
        package_name_fixed = None
        path_registry = None
    else:
        elc = ExtractorLoggingConfig(
            package_name,
            path_alternative_dest_folder=path_alternative_dest_folder,
        )
        # could raise strictyaml.YAMLValidationError
        elc.extract_db()
        package_name_fixed = elc.package_name
        path_registry = elc.path_extracted_db

    t_ret = (package_name_fixed, path_registry)

    return t_ret


def get_query_v1(conf):
    """Gather registry query. Originating from pyproject or cli.

    :param conf: pytest configuration class instance
    :type conf: pytest.Config
    :returns: query dict
    :rtype: dict[str, str | None]
    """
    if TYPE_CHECKING:
        d_conf: dict[str, str | None]
        fields: tuple[tuple[str | None], ...]
        name: str
        fallback: str | None
        qualname: str
        val: str | None

    d_conf = {}

    fields = (
        ("yaml_package_name", _get_fallback_package_name()),
        ("category", _get_fallback_category()),
        ("genre", None),
        ("flavor", None),
        ("version_no", None),
    )
    for name, fallback in fields:
        qualname = get_qualname(name)
        val = _get_arg_value(conf, qualname, fallback)
        d_conf[name] = val

    return d_conf


def get_yaml_v0(conf, path_f):
    """When session starts prepare, but do not apply, logging configuration.

    - If using plugin, configuration **must** be supplied: in ini or on cli

    - Extract logging config YAML from a package

    - Validate logging config YAML
       if exception, issue warning

    - Set validated raw logging config YAML to pytest stash

    :param conf: pytest configuration class instance
    :type conf: pytest.Config
    :param path_f: absolute path to temporary file
    :type path_f: pathlib.Path
    :returns: raw logging config YAML file
    :rtype: str | None

    .. seealso::

       shared temp folder

       https://hackebrot.github.io/pytest-tricks/shared_directory_xdist/

       https://github.com/realpython/pytest-mypy/pull/73/files

       https://github.com/tox-dev/filelock/pull/332

       https://github.com/realpython/pytest-mypy/blob/main/src/pytest_mypy/__init__.py

    """
    # Configuration **must** be supplied: in ini or on cli
    name = get_qualname("yaml_package_name")
    package_name = _get_arg_value(conf, name, _get_fallback_package_name())

    # relative path. For Windows support, must be posix
    name = get_qualname("package_data_folder_start")
    package_data_folder_start = _get_arg_value(
        conf,
        name,
        _get_fallback_package_data_folder_start(),
    )

    name = get_qualname("category")
    category = _get_arg_value(conf, name, _get_fallback_category())

    name = get_qualname("genre")
    fallback = None
    genre = _get_arg_value(conf, name, fallback)

    name = get_qualname("flavor")
    fallback = None
    flavor = _get_arg_value(conf, name, fallback)

    name = get_qualname("version_no")
    fallback = None
    version_no = _get_arg_value(conf, name, fallback)

    """Extract logging config YAML from a package.
    Validate logging config YAML. If exception, issue warning
    """
    path_dir = path_f.parent

    with (
        patch(  # defang. extract_to_config
            f"{IMPLEMENTATION_PACKAGE_NAME}.util.xdg_folder._get_path_config",
            return_value=path_dir,
        ),
        patch(
            f"{IMPLEMENTATION_PACKAGE_NAME}.logging_api._get_path_config",
            return_value=path_dir,
        ),
        patch(  # temp folder rather than :code:`$HOME/.local/share/[app]`
            f"{IMPLEMENTATION_PACKAGE_NAME}.logging_yaml_abc._get_path_config",
            return_value=path_dir,
        ),
    ):
        """removed exceptions. Set sane fallbacks
        logging_strict.exceptions.LoggingStrictPackageNameRequired
        logging_strict.exceptions.LoggingStrictPackageStartFolderNameRequired
        """
        try:
            # needs a dest_folder, patch logging_strict.logging_api._get_path_config
            api = LoggingConfigYaml(
                package_name,
                package_data_folder_start,
                category,
                genre=genre,
                flavor=flavor,
                version_no=version_no,
            )
            abspath_dir = api.dest_folder
            relpath_f = api.extract()
            # if relpath_f is not Path.as_posix, joinpath will fail
            abspath_f = abspath_dir.joinpath(relpath_f)
        except FileNotFoundError as exc:
            msg_warn = str(exc)
            is_extract = False
        except AssertionError as exc:
            # Search is not narrow enough. Many folders. Narrow package_data_folder_start
            msg_warn = str(exc)
            is_extract = False
        except ImportError:
            # package not installed
            msg_warn = (
                f"package_name {package_name} not installed. Before "
                "extracting package data, install the package into venv "
            )
            is_extract = False
        else:
            is_extract = True

        if is_extract is True:
            try:
                # validates raw logging config YAML
                str_yaml = as_str(abspath_f.parent, abspath_f.name)
                ret = str_yaml
            except s.YAMLValidationError:
                ret = None
        else:
            warnings.warn(msg_warn)
            ret = None

    return ret


def _parse_option_value(val):
    """Parse user supplied input. Must be a non-empty str

    Either from cli or an ini file

    :param val: raw user supplied value
    :type val: typing.Any
    :returns: Default None. option value
    :rtype: str | None
    """
    is_ng = val is None or not isinstance(val, str) or len(val.strip()) == 0
    if is_ng or val == "None":
        ret = None
    else:
        ret = val

    return ret


def _get_arg_value(conf, name, fallback):
    """Options must be passed to retrieve the logging config YAML file.
    Can either be specified on the cli or in an pytest supported ini file.

    For required args, if both cli and ini not provided return None

    :param conf: pytest configuration class instance
    :type conf: pytest.Config
    :param name: user supplied configuration argument name
    :type name: str
    :param fallback: fallback value
    :type fallback: str | None
    :returns: configuration value supplied by cli or config
    :rtype: str | None
    """
    # qualname = get_qualname(name)
    value_cli = conf.getoption(name)
    value_ini = conf.getini(name)

    if _parse_option_value(value_cli) is not None:
        # 1st priority
        ret = value_cli
    else:
        if _parse_option_value(value_ini) is not None:
            # 2nd priority
            ret = value_ini
        else:
            # fallback
            ret = fallback

    return ret


def get_temp_folder():
    """Get the temp folder. Would prefer in a randomized subfolder"""
    f = tempfile.NamedTemporaryFile(delete=False)
    path_f = Path(f.name)
    path_alternative_dest_folder = path_f.parent
    with suppress(OSError):
        f.close()
        path_f.unlink()

    return path_alternative_dest_folder
