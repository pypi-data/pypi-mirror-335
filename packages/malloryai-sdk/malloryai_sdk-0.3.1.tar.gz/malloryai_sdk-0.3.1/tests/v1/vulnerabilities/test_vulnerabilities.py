import pytest

pytestmark = pytest.mark.asyncio


async def test_list_vulnerabilities(api_client):
    """Test list_vulnerabilities() API call (async)."""
    response = await api_client.vulnerabilities.list_vulnerabilities()

    assert isinstance(response, dict), "Response is not a dictionary"
    assert "data" in response and isinstance(
        response["data"], list
    ), "Missing expected field: data"

    if response["data"]:
        first_vuln = response["data"][0]
        assert "cve_id" in first_vuln, "Missing expected field: cve_id"
        assert "description" in first_vuln, "Missing expected field: description"
        assert (
            "cvss_3_base_severity" in first_vuln
        ), "Missing expected field: cvss_3_base_severity"


async def test_get_vulnerability(api_client):
    """Test get_vulnerability() API call (async)."""
    vulnerability = await api_client.vulnerabilities.list_vulnerabilities(limit=1)
    assert isinstance(vulnerability, dict), "Response is not a dictionary"
    assert vulnerability["data"], "No vulnerabilities found to test with"
    vuln_id = vulnerability["data"][0]["cve_id"]
    response = await api_client.vulnerabilities.get_vulnerability(vuln_id)

    assert isinstance(response, dict)
    assert response["cve_id"] == vuln_id, "CVE ID does not match"
    assert "description" in response, "Missing expected field: description"
    assert "cvss_3_base_score" in response, "Missing expected field: cvss_3_base_score"
    assert (
        "cvss_3_base_severity" in response
    ), "Missing expected field: cvss_3_base_severity"


async def test_get_vulnerability_configurations(api_client):
    """Test get_vulnerability_configurations() API call (async)."""
    vulnerability = await api_client.vulnerabilities.list_vulnerabilities(limit=1)
    assert isinstance(vulnerability, dict), "Response is not a dictionary"
    assert vulnerability["data"], "No vulnerabilities found to test with"
    vuln_id = vulnerability["data"][0]["cve_id"]
    response = await api_client.vulnerabilities.get_vulnerability_configurations(
        vuln_id
    )

    if not response:
        pytest.skip("No configurations found for this vulnerability")

    assert isinstance(response, list), "Response is not a list"
    if response:
        first_config = response[0]
        required_fields = [
            "uuid",
            "created_at",
            "updated_at",
            "cpe_id",
            "set_id",
            "edition",
            "language",
            "sw_edition",
            "target_sw",
            "target_hw",
            "other",
            "versionStartExcluding",
            "versionStartIncluding",
            "versionEndExcluding",
            "versionEndIncluding",
            "updateStartIncluding",
            "updateEndIncluding",
            "is_vulnerable",
            "vendor",
            "vendor_display_name",
            "product_type",
            "product",
            "product_display_name",
            "cve_id",
        ]
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


async def test_get_vulnerability_detection_signatures(api_client):
    """Test get_vulnerability_detection_signatures() API call (async)."""
    vulnerability = await api_client.vulnerabilities.list_vulnerabilities(limit=1)
    assert isinstance(vulnerability, dict), "Response is not a dictionary"
    assert vulnerability["data"], "No vulnerabilities found to test with"
    vuln_id = vulnerability["data"][0]["cve_id"]
    response = await api_client.vulnerabilities.get_vulnerability_detection_signatures(
        vuln_id
    )

    if not response:
        pytest.skip("No detection signatures found for this vulnerability")

    assert isinstance(response, list), "Response is not a list"
    # If there are specific fields to validate, add them here.
    if response:
        first_config = response[0]
        required_fields = []  # Add required fields if any
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


async def test_get_vulnerability_exploitations(api_client):
    """Test get_vulnerability_exploitations() API call (async)."""
    vulnerability = await api_client.vulnerabilities.list_vulnerabilities(limit=1)
    assert isinstance(vulnerability, dict), "Response is not a dictionary"
    assert vulnerability["data"], "No vulnerabilities found to test with"
    vuln_id = vulnerability["data"][0]["cve_id"]
    response = await api_client.vulnerabilities.get_vulnerability_exploitations(vuln_id)

    if not response:
        pytest.skip("No exploitations found for this vulnerability")

    assert isinstance(response, list), "Response is not a list"
    # If there are specific fields to validate, add them here.
    if response:
        first_config = response[0]
        required_fields = []  # Add required fields if any
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


async def test_get_vulnerability_exploits(api_client):
    """Test get_vulnerability_exploits() API call (async)."""
    vulnerability = await api_client.vulnerabilities.list_vulnerabilities(limit=1)
    assert isinstance(vulnerability, dict), "Response is not a dictionary"
    assert vulnerability["data"], "No vulnerabilities found to test with"
    vuln_id = vulnerability["data"][0]["cve_id"]
    response = await api_client.vulnerabilities.get_vulnerability_exploits(vuln_id)

    if not response:
        pytest.skip("No exploits found for this vulnerability")

    assert isinstance(response, list), "Response is not a list"
    if response:
        first_config = response[0]
        required_fields = [
            "uuid",
            "description",
            "url",
            "maturity",
            "created_at",
            "updated_at",
            "vulnerabilities",
        ]
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


async def test_get_vulnerability_mentions(api_client):
    """Test get_vulnerability_mentions() API call (async)."""
    vulnerability = await api_client.vulnerabilities.list_vulnerabilities(limit=1)
    assert isinstance(vulnerability, dict), "Response is not a dictionary"
    assert vulnerability["data"], "No vulnerabilities found to test with"
    vuln_id = vulnerability["data"][0]["cve_id"]
    response = await api_client.vulnerabilities.get_vulnerability_mentions(vuln_id)

    if not response:
        pytest.skip("No mentions found for this vulnerability")

    assert isinstance(response, list), "Response is not a list"
    if response:
        first_config = response[0]
        required_fields = []  # Add required fields if any
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


async def test_get_vulnerabilities_mentions(api_client):
    """Test list_vulnerabilities_mentions() API call (async)."""
    response = await api_client.vulnerabilities.list_vulnerabilities_mentions(limit=5)

    assert isinstance(response, dict)
    assert "data" in response and isinstance(
        response["data"], list
    ), "Missing expected field: data"
    assert "total" in response and isinstance(
        response["total"], int
    ), "Missing expected field: total"
    assert "offset" in response and isinstance(
        response["offset"], int
    ), "Missing expected field: offset"
    assert "limit" in response and isinstance(
        response["limit"], int
    ), "Missing expected field: limit"

    if response["data"]:
        first_config = response["data"][0]
        required_fields = [
            "uuid",
            "created_at",
            "updated_at",
            "overview",
            "content_chunk_uuid",
            "reference_uuid",
            "reference_url",
            "vulnerability_uuid",
            "cve_id",
        ]
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


async def test_list_vulnerable_configurations(api_client):
    """Test list_vulnerable_configurations() API call (async)."""
    response = await api_client.vulnerabilities.list_vulnerable_configurations(limit=5)

    assert isinstance(response, dict), "Response is not a dictionary"
    assert "data" in response and isinstance(
        response["data"], list
    ), "Missing expected field: data"
    assert "total" in response and isinstance(
        response["total"], int
    ), "Missing expected field: total"
    assert "offset" in response and isinstance(
        response["offset"], int
    ), "Missing expected field: offset"
    assert "limit" in response and isinstance(
        response["limit"], int
    ), "Missing expected field: limit"

    if response["data"]:
        first_config = response["data"][0]
        required_fields = [
            "uuid",
            "created_at",
            "updated_at",
            "cpe_id",
            "set_id",
            "edition",
            "language",
            "sw_edition",
            "target_sw",
            "target_hw",
            "other",
            "versionStartExcluding",
            "versionStartIncluding",
            "versionEndExcluding",
            "versionEndIncluding",
            "updateStartIncluding",
            "updateEndIncluding",
            "is_vulnerable",
            "vendor",
            "vendor_display_name",
            "product_type",
            "product",
            "product_display_name",
            "cve_id",
        ]
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


def test_list_vulnerabilities_sync(api_client):
    """Test list_vulnerabilities_sync() API call (sync)."""
    response = api_client.vulnerabilities.list_vulnerabilities_sync()
    assert isinstance(response, dict), "Response is not a dictionary"
    assert "data" in response and isinstance(
        response["data"], list
    ), "Missing expected field: data"
    if response["data"]:
        first_vuln = response["data"][0]
        assert "cve_id" in first_vuln, "Missing expected field: cve_id"
        assert "description" in first_vuln, "Missing expected field: description"
        assert (
            "cvss_3_base_severity" in first_vuln
        ), "Missing expected field: cvss_3_base_severity"


def test_get_vulnerability_sync(api_client):
    """Test get_vulnerability_sync() API call (sync)."""
    vulnerability = api_client.vulnerabilities.list_vulnerabilities_sync(limit=1)
    assert isinstance(vulnerability, dict), "Response is not a dictionary"
    assert vulnerability["data"], "No vulnerabilities found to test with"
    vuln_id = vulnerability["data"][0]["cve_id"]
    response = api_client.vulnerabilities.get_vulnerability_sync(vuln_id)

    assert isinstance(response, dict)
    assert response["cve_id"] == vuln_id, "CVE ID does not match"
    assert "description" in response, "Missing expected field: description"
    assert "cvss_3_base_score" in response, "Missing expected field: cvss_3_base_score"
    assert (
        "cvss_3_base_severity" in response
    ), "Missing expected field: cvss_3_base_severity"


def test_get_vulnerability_configurations_sync(api_client):
    """Test get_vulnerability_configurations_sync() API call (sync)."""
    vulnerability = api_client.vulnerabilities.list_vulnerabilities_sync(limit=1)
    assert isinstance(vulnerability, dict), "Response is not a dictionary"
    assert vulnerability["data"], "No vulnerabilities found to test with"
    vuln_id = vulnerability["data"][0]["cve_id"]
    response = api_client.vulnerabilities.get_vulnerability_configurations_sync(vuln_id)

    if not response:
        pytest.skip("No configurations found for this vulnerability")
    assert isinstance(response, list), "Response is not a list"
    if response:
        first_config = response[0]
        required_fields = [
            "uuid",
            "created_at",
            "updated_at",
            "cpe_id",
            "set_id",
            "edition",
            "language",
            "sw_edition",
            "target_sw",
            "target_hw",
            "other",
            "versionStartExcluding",
            "versionStartIncluding",
            "versionEndExcluding",
            "versionEndIncluding",
            "updateStartIncluding",
            "updateEndIncluding",
            "is_vulnerable",
            "vendor",
            "vendor_display_name",
            "product_type",
            "product",
            "product_display_name",
            "cve_id",
        ]
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


def test_get_vulnerability_detection_signatures_sync(api_client):
    """Test get_vulnerability_detection_signatures_sync() API call (sync)."""
    vulnerability = api_client.vulnerabilities.list_vulnerabilities_sync(limit=1)
    assert isinstance(vulnerability, dict), "Response is not a dictionary"
    assert vulnerability["data"], "No vulnerabilities found to test with"
    vuln_id = vulnerability["data"][0]["cve_id"]
    response = api_client.vulnerabilities.get_vulnerability_detection_signatures_sync(
        vuln_id
    )

    if not response:
        pytest.skip("No detection signatures found for this vulnerability")
    assert isinstance(response, list), "Response is not a list"
    if response:
        first_config = response[0]
        required_fields = []  # Add required fields if needed
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


def test_get_vulnerability_exploitations_sync(api_client):
    """Test get_vulnerability_exploitations_sync() API call (sync)."""
    vulnerability = api_client.vulnerabilities.list_vulnerabilities_sync(limit=1)
    assert isinstance(vulnerability, dict), "Response is not a dictionary"
    assert vulnerability["data"], "No vulnerabilities found to test with"
    vuln_id = vulnerability["data"][0]["cve_id"]
    response = api_client.vulnerabilities.get_vulnerability_exploitations_sync(vuln_id)

    if not response:
        pytest.skip("No exploitations found for this vulnerability")
    assert isinstance(response, list), "Response is not a list"
    if response:
        first_config = response[0]
        required_fields = []  # Add required fields if needed
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


def test_get_vulnerability_exploits_sync(api_client):
    """Test get_vulnerability_exploits_sync() API call (sync)."""
    vulnerability = api_client.vulnerabilities.list_vulnerabilities_sync(limit=1)
    assert isinstance(vulnerability, dict), "Response is not a dictionary"
    assert vulnerability["data"], "No vulnerabilities found to test with"
    vuln_id = vulnerability["data"][0]["cve_id"]
    response = api_client.vulnerabilities.get_vulnerability_exploits_sync(vuln_id)

    if not response:
        pytest.skip("No exploits found for this vulnerability")
    assert isinstance(response, list), "Response is not a list"
    if response:
        first_config = response[0]
        required_fields = [
            "uuid",
            "description",
            "url",
            "maturity",
            "created_at",
            "updated_at",
            "vulnerabilities",
        ]
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


def test_get_vulnerability_mentions_sync(api_client):
    """Test get_vulnerability_mentions_sync() API call (sync)."""
    vulnerability = api_client.vulnerabilities.list_vulnerabilities_sync(limit=1)
    assert isinstance(vulnerability, dict), "Response is not a dictionary"
    assert vulnerability["data"], "No vulnerabilities found to test with"
    vuln_id = vulnerability["data"][0]["cve_id"]
    response = api_client.vulnerabilities.get_vulnerability_mentions_sync(vuln_id)

    if not response:
        pytest.skip("No mentions found for this vulnerability")
    assert isinstance(response, list), "Response is not a list"
    if response:
        first_config = response[0]
        required_fields = []  # Add required fields if needed
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


def test_get_vulnerabilities_mentions_sync(api_client):
    """Test list_vulnerabilities_mentions_sync() API call (sync)."""
    response = api_client.vulnerabilities.list_vulnerabilities_mentions_sync(limit=5)
    assert isinstance(response, dict)
    assert "data" in response and isinstance(
        response["data"], list
    ), "Missing expected field: data"
    assert "total" in response and isinstance(
        response["total"], int
    ), "Missing expected field: total"
    assert "offset" in response and isinstance(
        response["offset"], int
    ), "Missing expected field: offset"
    assert "limit" in response and isinstance(
        response["limit"], int
    ), "Missing expected field: limit"

    if response["data"]:
        first_config = response["data"][0]
        required_fields = [
            "uuid",
            "created_at",
            "updated_at",
            "overview",
            "content_chunk_uuid",
            "reference_uuid",
            "reference_url",
            "vulnerability_uuid",
            "cve_id",
        ]
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"


def test_list_vulnerable_configurations_sync(api_client):
    """Test list_vulnerable_configurations_sync() API call (sync)."""
    response = api_client.vulnerabilities.list_vulnerable_configurations_sync(limit=5)
    assert isinstance(response, dict), "Response is not a dictionary"
    assert "data" in response and isinstance(
        response["data"], list
    ), "Missing expected field: data"
    assert "total" in response and isinstance(
        response["total"], int
    ), "Missing expected field: total"
    assert "offset" in response and isinstance(
        response["offset"], int
    ), "Missing expected field: offset"
    assert "limit" in response and isinstance(
        response["limit"], int
    ), "Missing expected field: limit"

    if response["data"]:
        first_config = response["data"][0]
        required_fields = [
            "uuid",
            "created_at",
            "updated_at",
            "cpe_id",
            "set_id",
            "edition",
            "language",
            "sw_edition",
            "target_sw",
            "target_hw",
            "other",
            "versionStartExcluding",
            "versionStartIncluding",
            "versionEndExcluding",
            "versionEndIncluding",
            "updateStartIncluding",
            "updateEndIncluding",
            "is_vulnerable",
            "vendor",
            "vendor_display_name",
            "product_type",
            "product",
            "product_display_name",
            "cve_id",
        ]
        for field in required_fields:
            assert field in first_config, f"Missing expected field: {field}"
