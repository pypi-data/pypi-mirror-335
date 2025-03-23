"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

implementation v1 fixtures

"""

import pytest


@pytest.fixture(scope="session")
def impl_version_no():
    """Plugin implementation version_no

    :returns: version no
    :rtype: str
    """
    return "1"
