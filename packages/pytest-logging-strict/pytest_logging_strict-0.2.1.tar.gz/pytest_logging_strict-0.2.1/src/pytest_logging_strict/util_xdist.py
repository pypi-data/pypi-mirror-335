"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

xdist functions


"""

__all__ = (
    "is_xdist",
    "xdist_worker",
    "xdist_workerinput",
)


def is_xdist(config):
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


def xdist_worker(config):
    """Get pytest config passed to worker.

    :param config: pytest configuration
    :type config: pytest.Config
    :returns: xdist worker input
    :rtype: dict[str, typing.Any]
    """
    try:
        ret = {"input": xdist_workerinput(config)}
    except AttributeError:
        ret = {}

    return ret


def xdist_workerinput(node):
    """mypy complains that :py:class:`pytest.Config` does not have this
    attribute, but ``xdist.remote`` defines it in worker processes.

    :param node: A xdist worker
    :type node: xdist.workermanage.WorkerController | pytest.Config
    :returns: workerinput
    :rtype: typing.Any
    """
    try:
        ret = node.workerinput  # type: ignore[union-attr]
    except AttributeError:  # compat xdist < 2.0
        ret = node.slaveinput  # type: ignore[union-attr]

    return ret
