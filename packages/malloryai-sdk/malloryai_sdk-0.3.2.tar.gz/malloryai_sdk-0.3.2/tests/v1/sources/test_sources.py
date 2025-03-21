import pytest

pytestmark = pytest.mark.asyncio


async def test_list_sources(api_client):
    """Test list_sources() API call (async)."""
    response = await api_client.sources.list_sources()

    assert isinstance(response, dict)
    assert "sources" in response and isinstance(response["sources"], list)
    assert "count" in response and isinstance(response["count"], int)

    if response["sources"]:
        first_config = response["sources"][0]
        required_fields = ["slug"]
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


def test_list_sources_sync(api_client):
    """Test list_sources_sync() API call (sync)."""
    response = api_client.sources.list_sources_sync()

    assert isinstance(response, dict)
    assert "sources" in response and isinstance(response["sources"], list)
    assert "count" in response and isinstance(response["count"], int)

    if response["sources"]:
        first_config = response["sources"][0]
        required_fields = ["slug"]
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"
