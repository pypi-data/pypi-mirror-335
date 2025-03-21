import pytest

pytestmark = pytest.mark.asyncio


async def test_list_products(api_client):
    """Test list_products() API call (async)."""
    response = await api_client.products.list_products(limit=5)

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
            "type",
            "name",
            "display_name",
            "website",
            "upstream_id",
            "vendor",
            "vendor_display_name",
        ]
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


async def test_get_product(api_client):
    """Test get_product() API call (async)."""
    product = await api_client.products.list_products(limit=1)
    response = await api_client.products.get_product(product["data"][0]["uuid"])

    assert isinstance(response, dict)
    required_fields = [
        "uuid",
        "created_at",
        "updated_at",
        "type",
        "name",
        "display_name",
        "website",
        "upstream_id",
        "vendor",
        "vendor_display_name",
        "vulnerable_configurations",
    ]
    for field in required_fields:
        assert field in response, f"Missing expected field: {field}"


async def test_search_products(api_client):
    """Test search_products() API call (async)."""
    response = await api_client.products.search_products(limit=5)
    assert isinstance(response, dict)
    assert "data" in response and isinstance(response["data"], list)
    assert "total" in response and isinstance(response["total"], int)
    assert "offset" in response and isinstance(response["offset"], int)
    assert "limit" in response and isinstance(response["limit"], int)


def test_list_products_sync(api_client):
    """Test list_products_sync() API call (sync)."""
    response = api_client.products.list_products_sync(limit=5)

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
            "type",
            "name",
            "display_name",
            "website",
            "upstream_id",
            "vendor",
            "vendor_display_name",
        ]
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


def test_get_product_sync(api_client):
    """Test get_product_sync() API call (sync)."""
    product = api_client.products.list_products_sync(limit=1)
    response = api_client.products.get_product_sync(product["data"][0]["uuid"])

    assert isinstance(response, dict)
    required_fields = [
        "uuid",
        "created_at",
        "updated_at",
        "type",
        "name",
        "display_name",
        "website",
        "upstream_id",
        "vendor",
        "vendor_display_name",
        "vulnerable_configurations",
    ]
    for field in required_fields:
        assert field in response, f"Missing expected field: {field}"


def test_search_products_sync(api_client):
    """Test search_products_sync() API call (sync)."""
    response = api_client.products.search_products_sync(limit=5)
    assert isinstance(response, dict)
    assert "data" in response and isinstance(response["data"], list)
    assert "total" in response and isinstance(response["total"], int)
    assert "offset" in response and isinstance(response["offset"], int)
    assert "limit" in response and isinstance(response["limit"], int)
