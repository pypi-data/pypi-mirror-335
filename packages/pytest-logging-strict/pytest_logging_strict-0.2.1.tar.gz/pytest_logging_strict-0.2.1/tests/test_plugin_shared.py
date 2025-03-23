"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

WITHOUT using pytest-logging-strict, demonstrate fixture has_logging_occurred

"""

import copy

import pytest
from logging_strict.tech_niques.stream_capture import CaptureOutput
from logging_strict.util.check_type import is_not_ok

from pytest_logging_strict.plugin_shared import _check_out

testdata_check_out = (
    (
        [""],
        False,
        1,
        ["Nothing captured"],
    ),
    (
        ["Hello World", "Thanks for all the fish"],
        True,
        2,
        ["Hello World", "Thanks for all the fish"],
    ),
)
ids_check_out = (
    "no output",
    "two lines of output",
)


@pytest.mark.parametrize(
    "output, outcome_expected, line_count_expected, expected_capture",
    testdata_check_out,
    ids=ids_check_out,
)
def test_check_out(output, outcome_expected, line_count_expected, expected_capture):
    """Testable guts of fixture has_logging_occurred"""
    # pytest --showlocals -r a -vv --log-level INFO -k "test_check_out" tests
    with CaptureOutput() as cm:
        outcome_actual = _check_out(output)
    str_out = cm.stdout
    assert outcome_actual is outcome_expected

    lines_before = str_out.split("\n")
    lines_after = copy.deepcopy(lines_before)
    # remove empty lines
    idxs = []
    for idx, line in enumerate(lines_before):
        if is_not_ok(line):
            idxs.append(idx)
    for idx in reversed(idxs):
        del lines_after[idx]
    line_count_actual = len(lines_after)
    assert line_count_actual == line_count_expected

    # logging formatting modifies each line. But somewhere within is the log message
    expected_capture_count = len(expected_capture)
    for idx, line in enumerate(lines_after):
        if expected_capture_count >= idx + 1:
            line_expected = expected_capture[idx]
            assert line_expected in line
        else:
            # mismatch line counts
            reason = f"expected_capture_count < actual lines count {line_count_actual}"
            pytest.xfail(reason)


def test_fixture_has_logging_occurred(pytester):
    """Minimal detect logging occurred example"""
    # pytest --showlocals -r a -vv --log-level INFO -k "test_fixture_has_logging_occurred" tests
    path_pytester = pytester.path  # noqa: F841
    lst_plugins = pytester.plugins  # noqa: F841
    name = "test_has_logging_occurred"
    test_text = """
            import logging
            def test_fcn_has_logging_occurred(caplog, has_logging_occurred):
                caplog.set_level(logging.INFO)
                logger = logging.getLogger()
                assert not has_logging_occurred()
                logger.info("Hi there")
                assert has_logging_occurred()

        """
    pytester.makepyfile(**{name: test_text})

    # empty conftest.py
    conftest_text = ""
    pytester.makeconftest(conftest_text)

    args = (
        "--showlocals",
        "-vv",
        "-k",
        "test_fcn_has_logging_occurred",
    )
    kwargs = {}
    run_result = pytester.runpytest_subprocess(*args, **kwargs)

    outcomes = run_result.parseoutcomes()  # noqa: F841
    exit_code = run_result.ret
    assert exit_code == 0
