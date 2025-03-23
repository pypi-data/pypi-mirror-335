"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

.. py:data:: item_marker
   :type: str
   :value: "logging_package_name"

   Name of a pytest marker. Takes one argument, a dotted path logger
   handlers package name
"""

import pytest

item_marker = "logging_package_name"


def _check_out(output: list[str]) -> bool:
    """Separated to be testable and without printing a header line"""
    if output == [""]:
        print("Nothing captured")
        ret = False
    else:
        for i in range(len(output)):
            print(f"{i}: {output[i]}")
        ret = True

    return ret


@pytest.fixture()
def has_logging_occurred(caplog: pytest.LogCaptureFixture) -> bool:
    """Display caplog capture text.

    Usage

    .. code-block: text

       import pytest
       # import your packages underscored name from package's constants module
       g_app_name = "my_package"

       @pytest.mark.logging_package_name(g_app_name)
       def test_something(logging_strict, has_logging_occurred):
           t_two = logging_strict()
           logger, loggers = t_two

           logger.info("Hi there")

           assert has_logging_occurred()

    .. seealso::

       https://github.com/pytest-dev/pytest/discussions/11011
       https://github.com/thebuzzstop/pytest_caplog/tree/master
       `pass params fixture <https://stackoverflow.com/a/44701916>`_

    """

    def _method() -> bool:
        """Check if there is at least one log message. Print log messages.

        :returns: True if logging occurred otherwise False
        :rtype: bool
        """
        output = caplog.text.rstrip("\n").split(sep="\n")
        print("\nCAPLOG:")
        ret = _check_out(output)

        return ret

    return _method
