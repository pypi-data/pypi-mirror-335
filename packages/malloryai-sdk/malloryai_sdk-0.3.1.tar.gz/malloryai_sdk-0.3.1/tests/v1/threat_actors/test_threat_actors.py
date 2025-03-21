import pytest

pytestmark = pytest.mark.asyncio


async def test_list_actors(api_client):
    """Test list_threat_actors() API call (async)."""
    response = await api_client.threat_actors.list_threat_actors()

    assert isinstance(response, dict)
    assert "data" in response and isinstance(response["data"], list)

    if response["data"]:
        first_actor = response["data"][0]
        print(first_actor)
        assert "uuid" in first_actor
        assert "name" in first_actor
        assert "display_name" in first_actor
        assert "misp_uuid" in first_actor
        assert "created_at" in first_actor
        assert "updated_at" in first_actor


async def test_get_threat_actor(api_client):
    """Test get_threat_actor() API call (async)."""
    actor_id = "ghostemperor"
    response = await api_client.threat_actors.get_threat_actor(actor_id)

    assert isinstance(response, dict)
    actor_data = response
    # Either name matches or display_name (case-insensitive) matches
    assert (
        actor_data["name"] == actor_id
        or actor_data["display_name"].lower() == actor_id.lower()
    )
    assert "uuid" in actor_data
    assert "mentions" in actor_data and isinstance(actor_data["mentions"], list)

    if actor_data["mentions"]:
        first_mention = actor_data["mentions"][0]
        assert "overview" in first_mention
        assert "reference_url" in first_mention


async def test_list_threat_actors_mentioned(api_client):
    """Test list_threat_actors_mentioned() API call (async)."""
    response = await api_client.threat_actors.list_threat_actors_mentioned(limit=5)

    assert isinstance(response, dict)
    assert "data" in response and isinstance(response["data"], list)
    assert "total" in response and isinstance(response["total"], int)
    assert "offset" in response and isinstance(response["offset"], int)
    assert "limit" in response and isinstance(response["limit"], int)

    if response["data"]:
        first_config = response["data"][0]
        required_fields = [
            "uuid",
            "overview",
            "created_at",
            "updated_at",
            "published_at",
            "collected_at",
            "content_chunk_uuid",
            "reference_uuid",
            "reference_url",
            "threat_actor_uuid",
            "threat_actor_name",
        ]
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


def test_list_actors_sync(api_client):
    """Test list_threat_actors_sync() API call (sync)."""
    response = api_client.threat_actors.list_threat_actors_sync()

    assert isinstance(response, dict)
    assert "data" in response and isinstance(response["data"], list)

    if response["data"]:
        first_actor = response["data"][0]
        assert "uuid" in first_actor
        assert "name" in first_actor
        assert "display_name" in first_actor
        assert "misp_uuid" in first_actor
        assert "created_at" in first_actor
        assert "updated_at" in first_actor


def test_get_threat_actor_sync(api_client):
    """Test get_threat_actor_sync() API call (sync)."""
    actor_id = "ghostemperor"
    response = api_client.threat_actors.get_threat_actor_sync(actor_id)

    assert isinstance(response, dict)
    actor_data = response
    assert (
        actor_data["name"] == actor_id
        or actor_data["display_name"].lower() == actor_id.lower()
    )
    assert "uuid" in actor_data
    assert "mentions" in actor_data and isinstance(actor_data["mentions"], list)

    if actor_data["mentions"]:
        first_mention = actor_data["mentions"][0]
        assert "overview" in first_mention
        assert "reference_url" in first_mention


def test_list_threat_actors_mentioned_sync(api_client):
    """Test list_threat_actors_mentioned_sync() API call (sync)."""
    response = api_client.threat_actors.list_threat_actors_mentioned_sync(limit=5)
    print(response)

    assert isinstance(response, dict)
    assert "data" in response and isinstance(response["data"], list)
    assert "total" in response and isinstance(response["total"], int)
    assert "offset" in response and isinstance(response["offset"], int)
    assert "limit" in response and isinstance(response["limit"], int)

    if response["data"]:
        first_config = response["data"][0]
        required_fields = [
            "uuid",
            "overview",
            "created_at",
            "updated_at",
            "published_at",
            "collected_at",
            "content_chunk_uuid",
            "reference_uuid",
            "reference_url",
            "threat_actor_uuid",
            "threat_actor_name",
        ]
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"
