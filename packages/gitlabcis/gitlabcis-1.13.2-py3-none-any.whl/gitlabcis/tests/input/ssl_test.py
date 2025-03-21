# -----------------------------------------------------------------------------

import builtins
from unittest.mock import patch

import pytest

from gitlabcis.cli.auth import GitlabCIS

# -----------------------------------------------------------------------------


# mock auth
@pytest.fixture
def mock_gitlab():
    with patch('gitlabcis.cli.auth.gitlab') as mock:
        yield mock


# skip admin warning
@pytest.fixture(autouse=True)
def mock_input(monkeypatch):
    monkeypatch.setattr(builtins, 'input', lambda _: 'y')


def test_no_verify_ssl(mock_gitlab):
    gitlab_cis = GitlabCIS(
        'https://gitlab.com/destination/project', token='fake-token',
        ssl_verify=False)
    assert gitlab_cis.ssl_verify is False
