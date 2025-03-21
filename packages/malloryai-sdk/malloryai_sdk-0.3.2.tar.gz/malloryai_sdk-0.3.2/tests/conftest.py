import os
import pytest
import logging
from malloryai.sdk.api.v1.api import MalloryIntelligenceClient

# Only load .env if the API key isn’t already set
if not os.getenv("MALLORY_API_KEY"):
    from dotenv import load_dotenv

    load_dotenv()

API_KEY = os.getenv("MALLORY_API_KEY", "test_api_key")


@pytest.fixture
def api_client():
    """Fixture to initialize MalloryAPIClient with test API key."""
    logger = logging.getLogger("test_logger")
    return MalloryIntelligenceClient(api_key=API_KEY, logger=logger)
