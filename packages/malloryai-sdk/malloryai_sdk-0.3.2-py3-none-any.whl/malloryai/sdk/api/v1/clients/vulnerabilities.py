from typing import List, Dict, Any, Optional
from malloryai.sdk.api.v1.decorators.sorting import validate_sorting
from malloryai.sdk.api.v1.http_client import HttpClient


class VulnerabilitiesClient:
    """Client for managing vulnerabilities."""

    LIST_VULNERABILITIES_PATH = "/vulnerabilities"
    VULNERABILITY_DETAIL_PATH = "/vulnerabilities/{identifier}"
    VULNERABILITY_CONFIGURATIONS_PATH = "/vulnerabilities/{identifier}/configurations"
    VULNERABILITY_DETECTION_SIGNATURES_PATH = (
        "/vulnerabilities/{identifier}/detection_signatures"
    )
    VULNERABILITY_EXPLOITATIONS_PATH = "/vulnerabilities/{identifier}/exploitations"
    VULNERABILITY_EXPLOITS_PATH = "/vulnerabilities/{identifier}/exploits"
    VULNERABILITY_MENTIONS_PATH = "/vulnerabilities/{identifier}/mentions"
    LIST_VULNERABLE_CONFIGURATIONS_PATH = "/vulnerable_configurations"
    VULNERABLE_CONFIGURATION_DETAIL_PATH = "/vulnerable_configurations/{identifier}"
    SEARCH_VULNERABLE_CONFIGURATIONS_PATH = "/vulnerable_configurations/search"
    LIST_VULNERABILITIES_MENTIONS_PATH = "/mentions/vulnerabilities"

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    @validate_sorting
    async def list_vulnerabilities(
        self,
        filter: Optional[str] = "",
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """
        List vulnerabilities.
        :param filter: Filter query.
        :param offset: Offset for pagination.
        :param limit: Limit for pagination.
        :param sort: Sorting field.
        :param order: Sorting order.
        :return: List of vulnerabilities.
        """
        params = {
            "filter": filter,
            "offset": offset,
            "limit": limit,
            "sort": sort,
            "order": order,
        }
        return await self.http_client.get(self.LIST_VULNERABILITIES_PATH, params=params)

    async def get_vulnerability(self, identifier: str) -> Dict[str, Any]:
        """
        Get vulnerability by identifier.
        :param identifier: Vulnerability identifier (CVE, UUID).
        :return: Vulnerability details.
        """
        path = self.VULNERABILITY_DETAIL_PATH.format(identifier=identifier)
        return await self.http_client.get(path)

    async def get_vulnerability_configurations(self, identifier: str) -> Dict[str, Any]:
        """
        Get vulnerability configurations.
        :param identifier: Vulnerability identifier (CVE, UUID).
        :return: Vulnerability configurations.
        """
        path = self.VULNERABILITY_CONFIGURATIONS_PATH.format(identifier=identifier)
        return await self.http_client.get(path)

    async def get_vulnerability_detection_signatures(
        self, identifier: str
    ) -> Dict[str, Any]:
        """
        Get vulnerability detection signatures.
        :param identifier: Vulnerability identifier (CVE, UUID).
        :return: Vulnerability detection signatures.
        """
        path = self.VULNERABILITY_DETECTION_SIGNATURES_PATH.format(
            identifier=identifier
        )
        return await self.http_client.get(path)

    async def get_vulnerability_exploitations(self, identifier: str) -> Dict[str, Any]:
        """
        Get vulnerability exploitations.
        :param identifier: Vulnerability identifier (CVE, UUID).
        :return: Vulnerability exploitations.
        """
        path = self.VULNERABILITY_EXPLOITATIONS_PATH.format(identifier=identifier)
        return await self.http_client.get(path)

    async def get_vulnerability_exploits(self, identifier: str) -> Dict[str, Any]:
        """
        Get vulnerability exploits.
        :param identifier: Vulnerability identifier (CVE, UUID).
        :return: Vulnerability exploits.
        """
        path = self.VULNERABILITY_EXPLOITS_PATH.format(identifier=identifier)
        return await self.http_client.get(path)

    async def get_vulnerability_mentions(self, identifier: str) -> Dict[str, Any]:
        """
        Get vulnerability mentions.
        :param identifier: Vulnerability identifier (CVE, UUID).
        :return: Vulnerability mentions.
        """
        path = self.VULNERABILITY_MENTIONS_PATH.format(identifier=identifier)
        return await self.http_client.get(path)

    @validate_sorting
    async def list_vulnerable_configurations(
        self,
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """
        List vulnerable configurations.
        :param offset: Offset for pagination.
        :param limit: Limit for pagination.
        :param sort: Sorting field.
        :param order: Sorting order.
        :return: List of vulnerable configurations.
        """
        params = {"offset": offset, "limit": limit, "sort": sort, "order": order}
        return await self.http_client.get(
            self.LIST_VULNERABLE_CONFIGURATIONS_PATH, params=params
        )

    async def get_vulnerable_configuration(self, identifier: str) -> Dict[str, Any]:
        """
        Get vulnerable configuration by identifier.
        :param identifier: Vulnerable configuration identifier (UUID).
        :return: Vulnerable configuration details.
        """
        path = self.VULNERABLE_CONFIGURATION_DETAIL_PATH.format(identifier=identifier)
        return await self.http_client.get(path)

    @validate_sorting(
        sort_pattern="^(created_at|updated_at|published_at|collected_at)$"
    )
    async def search_vulnerable_configurations(
        self,
        vendor: str,
        product: str,
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """
        Search vulnerable configurations.
        :param vendor: Vendor name.
        :param product: Product name.
        :param offset: Offset for pagination.
        :param limit: Limit for pagination.
        :param sort: Sorting field.
        :param order: Sorting order.
        :return: List of vulnerable configurations.
        """
        payload = {"vendor": vendor, "product": product}
        params = {"offset": offset, "limit": limit, "sort": sort, "order": order}
        return await self.http_client.post(
            self.SEARCH_VULNERABLE_CONFIGURATIONS_PATH, json=payload, params=params
        )

    @validate_sorting(
        sort_pattern="^(created_at|updated_at|published_at|collected_at)$"
    )
    async def list_vulnerabilities_mentions(
        self,
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """
        List vulnerabilities mentions.
        :param offset: Offset for pagination.
        :param limit: Limit for pagination.
        :param sort: Sorting field.
        :param order: Sorting order.
        :return: List of vulnerabilities mentions.
        """
        params = {"offset": offset, "limit": limit, "sort": sort, "order": order}
        return await self.http_client.get(
            self.LIST_VULNERABILITIES_MENTIONS_PATH, params=params
        )

    @validate_sorting
    def list_vulnerabilities_sync(
        self,
        filter: Optional[str] = "",
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
    ) -> List[Dict[str, Any]]:
        params = {
            "filter": filter,
            "offset": offset,
            "limit": limit,
            "sort": sort,
            "order": order,
        }
        return self.http_client.get_sync(self.LIST_VULNERABILITIES_PATH, params=params)

    def get_vulnerability_sync(self, identifier: str) -> Dict[str, Any]:
        path = self.VULNERABILITY_DETAIL_PATH.format(identifier=identifier)
        return self.http_client.get_sync(path)

    def get_vulnerability_configurations_sync(self, identifier: str) -> Dict[str, Any]:
        path = self.VULNERABILITY_CONFIGURATIONS_PATH.format(identifier=identifier)
        return self.http_client.get_sync(path)

    def get_vulnerability_detection_signatures_sync(
        self, identifier: str
    ) -> Dict[str, Any]:
        path = self.VULNERABILITY_DETECTION_SIGNATURES_PATH.format(
            identifier=identifier
        )
        return self.http_client.get_sync(path)

    def get_vulnerability_exploitations_sync(self, identifier: str) -> Dict[str, Any]:
        path = self.VULNERABILITY_EXPLOITATIONS_PATH.format(identifier=identifier)
        return self.http_client.get_sync(path)

    def get_vulnerability_exploits_sync(self, identifier: str) -> Dict[str, Any]:
        path = self.VULNERABILITY_EXPLOITS_PATH.format(identifier=identifier)
        return self.http_client.get_sync(path)

    def get_vulnerability_mentions_sync(self, identifier: str) -> Dict[str, Any]:
        path = self.VULNERABILITY_MENTIONS_PATH.format(identifier=identifier)
        return self.http_client.get_sync(path)

    @validate_sorting
    def list_vulnerable_configurations_sync(
        self,
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
    ) -> List[Dict[str, Any]]:
        params = {"offset": offset, "limit": limit, "sort": sort, "order": order}
        return self.http_client.get_sync(
            self.LIST_VULNERABLE_CONFIGURATIONS_PATH, params=params
        )

    def get_vulnerable_configuration_sync(self, identifier: str) -> Dict[str, Any]:
        path = self.VULNERABLE_CONFIGURATION_DETAIL_PATH.format(identifier=identifier)
        return self.http_client.get_sync(path)

    @validate_sorting
    def search_vulnerable_configurations_sync(
        self,
        vendor: str,
        product: str,
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
    ) -> List[Dict[str, Any]]:
        payload = {"vendor": vendor, "product": product}
        params = {"offset": offset, "limit": limit, "sort": sort, "order": order}
        return self.http_client.post_sync(
            self.SEARCH_VULNERABLE_CONFIGURATIONS_PATH, json=payload, params=params
        )

    @validate_sorting
    def list_vulnerabilities_mentions_sync(
        self,
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
    ) -> List[Dict[str, Any]]:
        params = {"offset": offset, "limit": limit, "sort": sort, "order": order}
        return self.http_client.get_sync(
            self.LIST_VULNERABILITIES_MENTIONS_PATH, params=params
        )
