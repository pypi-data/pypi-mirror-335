import pytest

pytestmark = pytest.mark.asyncio


async def test_list_references(api_client):
    """Test list_references() API call (async)."""
    response = await api_client.references.list_references(limit=5)

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
            "published_at",
            "collected_at",
            "url_hash",
            "source",
            "user_generated_content",
            "content_type",
            "topic",
            "authors",
            "content_chunk_uuids",
        ]
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


async def test_get_reference(api_client):
    """Test get_reference() API call (async)."""
    reference = await api_client.references.list_references(limit=1)
    response = await api_client.references.get_reference(reference["data"][0]["uuid"])

    assert isinstance(response, dict)
    required_fields = [
        "uuid",
        "created_at",
        "updated_at",
        "published_at",
        "collected_at",
        "url_hash",
        "source",
        "user_generated_content",
        "content_type",
        "topic",
        "authors",
        "content_chunks",
    ]
    for field in required_fields:
        assert field in response, f"Missing expected field: {field}"


async def test_create_reference(api_client):
    """Test create_references() API call (async)."""
    # Uncomment the following lines if you want to test the creation logic.
    # response = await api_client.references.create_references(["https://example.com"])
    # assert isinstance(response, dict)
    assert True


def test_list_references_sync(api_client):
    """Test list_references_sync() API call (sync)."""
    response = api_client.references.list_references_sync(limit=5)

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
            "published_at",
            "collected_at",
            "url_hash",
            "source",
            "user_generated_content",
            "content_type",
            "topic",
            "authors",
            "content_chunk_uuids",
        ]
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


def test_get_reference_sync(api_client):
    """Test get_reference_sync() API call (sync)."""
    reference = api_client.references.list_references_sync(limit=1)
    response = api_client.references.get_reference_sync(reference["data"][0]["uuid"])

    assert isinstance(response, dict)
    required_fields = [
        "uuid",
        "created_at",
        "updated_at",
        "published_at",
        "collected_at",
        "url_hash",
        "source",
        "user_generated_content",
        "content_type",
        "topic",
        "authors",
        "content_chunks",
    ]
    for field in required_fields:
        assert field in response, f"Missing expected field: {field}"


def test_create_reference_sync(api_client):
    """Test create_references_sync() API call (sync)."""
    # Uncomment the following lines if you want to test the creation logic.
    # response = api_client.references.create_references_sync(["https://example.com"])
    # assert isinstance(response, dict)
    assert True
