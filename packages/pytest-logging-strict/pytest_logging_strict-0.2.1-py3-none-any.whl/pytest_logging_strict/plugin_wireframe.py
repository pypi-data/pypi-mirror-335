"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

pytest plugin shared wireframe for choosing which implementation to run

The non-overlapping plugin_v0 and plugin_v1 fixtures are both imported. This
is not ideal. Hoping would lessen the issue of coverage not finding
those fixtures.

But there was no improvement. All fixtures are not spotted by coverage.
Without accurate coverage reports, don't know what code blocks are not covered

"""

from pytest_logging_strict.plugin_v0 import (  # noqa: F401
    get_d_config,
    logging_strict_get,
    logging_strict_get_stash_path,
)
from pytest_logging_strict.plugin_v1 import (  # noqa: F401
    registry_get,
    registry_get_stash_path,
    registry_validate,
)

from .util import (
    IMPLEMENTATION_VERSION_NO_DEFAULT,
    _get_arg_value,
    get_qualname,
    update_parser,
)
from .util_xdist import xdist_worker


def pytest_addoption(parser):
    """The config options are search filters. To aid in finding a raw
    logging strict config YAML. The logging configuration is then always known,
    strictly validated against a schema, DRY, and hopefully UX intuitive.

    - which package to configure logging for.
    - choose logging config YAML

    :param parser: pytest argparse parser
    :type parser: pytest.Parser
    """
    update_parser(parser)


def pytest_configure(config):
    """pytest hook for plugin configuration.

    There are two implementations. For the fixtures to be found,
    need to move variable scope from local to global

    :param config: pytest configuration
    :type config: pytest.Config
    """
    global get_d_config_initialize
    global logging_strict

    xdist_worker_ = xdist_worker(config)
    impl_version = _get_arg_value(
        config,
        get_qualname("impl_version_no"),
        IMPLEMENTATION_VERSION_NO_DEFAULT,
    )

    if impl_version == IMPLEMENTATION_VERSION_NO_DEFAULT:
        # latest implementation
        # change fixture variable scope from function --> global
        from pytest_logging_strict.plugin_v1 import (
            _configure,
            get_d_config_initialize,
            logging_strict,
        )

        _configure(config, xdist_worker_)
    else:
        # previous implementations
        # change fixture variable scope from function --> global
        from pytest_logging_strict.plugin_v0 import (
            _configure,
            get_d_config_initialize,
            logging_strict,
        )

        _configure(config, xdist_worker_)
