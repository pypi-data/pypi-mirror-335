from typing import List, Dict, Any
from malloryai.sdk.api.v1.decorators.sorting import validate_sorting
from malloryai.sdk.api.v1.http_client import HttpClient


class ReferencesClient:
    """Client for managing references."""

    LIST_REFERENCES_PATH = "/references"
    REFERENCE_DETAIL_PATH = "/references/{identifier}"
    CREATE_REFERENCES_PATH = "/references"

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    @validate_sorting(
        sort_pattern="^(published_at|collected_at|created_at|updated_at)$"
    )
    async def list_references(
        self,
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
        filter: str = "",
    ) -> List[Dict[str, Any]]:
        """
        List references.
        :param offset: Offset for pagination.
        :param limit: Limit for pagination.
        :param sort: Sorting field.
        :param order: Sorting order.
        :param filter: Filter by field.
        :return: List of references.
        """
        params = {
            "offset": offset,
            "limit": limit,
            "sort": sort,
            "order": order,
            "filter": filter,
        }
        return await self.http_client.get(self.LIST_REFERENCES_PATH, params=params)

    async def get_reference(self, identifier: str) -> Dict[str, Any]:
        """
        Get a reference by identifier.
        :param identifier: Reference identifier.
        :return: Reference.
        """
        path = self.REFERENCE_DETAIL_PATH.format(identifier=identifier)
        return await self.http_client.get(path)

    async def create_references(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Create references from URLs.
        :param urls: URLs to create references from.
        :return: References.
        """
        return await self.http_client.post(
            self.CREATE_REFERENCES_PATH, json={"urls": urls}
        )

    def list_references_sync(
        self,
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
        filter: str = "",
    ) -> List[Dict[str, Any]]:
        """
        Synchronous version of list_references.
        :param offset: Offset for pagination.
        :param limit: Limit for pagination.
        :param sort: Sorting field.
        :param order: Sorting order.
        :param filter: Filter by field.
        :return: List of references.
        """
        params = {
            "offset": offset,
            "limit": limit,
            "sort": sort,
            "order": order,
            "filter": filter,
        }
        return self.http_client.get_sync(self.LIST_REFERENCES_PATH, params=params)

    def get_reference_sync(self, identifier: str) -> Dict[str, Any]:
        """
        Synchronous version of get_reference.
        :param identifier: Reference identifier.
        :return: Reference.
        """
        path = self.REFERENCE_DETAIL_PATH.format(identifier=identifier)
        return self.http_client.get_sync(path)

    def create_references_sync(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Synchronous version of create_references.
        :param urls: URLs to create references from.
        :return: References.
        """
        return self.http_client.post_sync(
            self.CREATE_REFERENCES_PATH, json={"urls": urls}
        )
