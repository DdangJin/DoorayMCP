"""Pytest configuration and fixtures."""

import os
import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    os.environ["DOORAY_API_KEY"] = "test_api_key"
    os.environ["DOORAY_BASE_URL"] = "https://api.dooray.com"
    os.environ["DOORAY_LOG_LEVEL"] = "DEBUG"


@pytest.fixture
def sample_dooray_response():
    """Sample Dooray API response for testing."""
    return {
        "header": {
            "isSuccessful": True,
            "resultCode": 0,
            "resultMessage": "SUCCESS"
        },
        "result": []
    }