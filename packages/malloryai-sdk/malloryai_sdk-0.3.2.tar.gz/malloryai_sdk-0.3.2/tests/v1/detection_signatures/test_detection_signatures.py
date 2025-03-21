import pytest

pytestmark = pytest.mark.asyncio


async def test_list_detection_signatures(api_client):
    """Test list_detection_signatures() API call (async)."""
    response = await api_client.detection_signatures.list_detection_signatures(limit=5)

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
            "source",
            "method",
            "description",
            "upstream_id",
        ]
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


async def test_get_detection_signature(api_client):
    """Test get_detection_signature() API call (async)."""
    detection_signature = (
        await api_client.detection_signatures.list_detection_signatures(limit=1)
    )
    response = await api_client.detection_signatures.get_detection_signature(
        detection_signature["data"][0]["uuid"]
    )

    assert isinstance(response, dict)
    required_fields = [
        "uuid",
        "created_at",
        "updated_at",
        "source",
        "method",
        "description",
        "upstream_id",
        "vulnerability_uuids",
    ]
    for field in required_fields:
        assert field in response, f"Missing expected field: {field}"


def test_list_detection_signatures_sync(api_client):
    """Test list_detection_signatures_sync() API call (sync)."""
    response = api_client.detection_signatures.list_detection_signatures_sync(limit=5)

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
            "source",
            "method",
            "description",
            "upstream_id",
        ]
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


def test_get_detection_signature_sync(api_client):
    """Test get_detection_signature_sync() API call (sync)."""
    detection_signature = (
        api_client.detection_signatures.list_detection_signatures_sync(limit=1)
    )
    response = api_client.detection_signatures.get_detection_signature_sync(
        detection_signature["data"][0]["uuid"]
    )

    assert isinstance(response, dict)
    required_fields = [
        "uuid",
        "created_at",
        "updated_at",
        "source",
        "method",
        "description",
        "upstream_id",
        "vulnerability_uuids",
    ]
    for field in required_fields:
        assert field in response, f"Missing expected field: {field}"
