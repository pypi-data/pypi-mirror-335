import pytest

pytestmark = pytest.mark.asyncio


async def test_list_vendors(api_client):
    """Test list_vendors() API call (async)."""
    response = await api_client.vendors.list_vendors(limit=5)

    assert isinstance(response, dict)
    assert "data" in response and isinstance(response["data"], list)
    assert "total" in response and isinstance(response["total"], int)
    assert "offset" in response and isinstance(response["offset"], int)
    assert "limit" in response and isinstance(response["limit"], int)

    if response["data"]:
        first_config = response["data"][0]
        required_fields = [
            "uuid",
            "created_at",
            "updated_at",
            "name",
            "display_name",
            "website",
            "description",
        ]
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


async def test_get_vendor(api_client):
    """Test get_vendor() API call (async)."""
    vendor = await api_client.vendors.list_vendors(limit=1)
    response = await api_client.vendors.get_vendor(vendor["data"][0]["uuid"])

    assert isinstance(response, dict)
    required_fields = [
        "uuid",
        "created_at",
        "updated_at",
        "name",
        "display_name",
        "website",
        "description",
    ]
    for field in required_fields:
        assert field in response, f"Missing expected field: {field}"


def test_list_vendors_sync(api_client):
    """Test list_vendors_sync() API call (sync)."""
    response = api_client.vendors.list_vendors_sync(limit=5)

    assert isinstance(response, dict)
    assert "data" in response and isinstance(response["data"], list)
    assert "total" in response and isinstance(response["total"], int)
    assert "offset" in response and isinstance(response["offset"], int)
    assert "limit" in response and isinstance(response["limit"], int)

    if response["data"]:
        first_config = response["data"][0]
        required_fields = [
            "uuid",
            "created_at",
            "updated_at",
            "name",
            "display_name",
            "website",
            "description",
        ]
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


def test_get_vendor_sync(api_client):
    """Test get_vendor_sync() API call (sync)."""
    vendor = api_client.vendors.list_vendors_sync(limit=1)
    response = api_client.vendors.get_vendor_sync(vendor["data"][0]["uuid"])

    assert isinstance(response, dict)
    required_fields = [
        "uuid",
        "created_at",
        "updated_at",
        "name",
        "display_name",
        "website",
        "description",
    ]
    for field in required_fields:
        assert field in response, f"Missing expected field: {field}"
