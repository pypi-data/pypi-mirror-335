"""
Global fixture

Version: 5.4.0
Date updated: 21/03/2025 (dd/mm/yyyy)
"""

import pytest


@pytest.fixture(scope="session")
def test_fixture_session():
    """This cache the fixture for current test session"""
    return None
