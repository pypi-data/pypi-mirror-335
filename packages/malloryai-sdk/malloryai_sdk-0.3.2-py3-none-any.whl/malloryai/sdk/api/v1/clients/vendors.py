from typing import List, Dict, Any
from malloryai.sdk.api.v1.decorators.sorting import validate_sorting
from malloryai.sdk.api.v1.http_client import HttpClient


class VendorsClient:
    """Client for managing vendors."""

    LIST_VENDORS_PATH = "/vendors"
    VENDOR_DETAIL_PATH = "/vendors/{identifier}"

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    @validate_sorting(sort_pattern="^(name|created_at|updated_at)$")
    async def list_vendors(
        self,
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
        filter: str = "",
    ) -> List[Dict[str, Any]]:
        """
        List vendors.
        :param offset: Offset for pagination.
        :param limit: Limit for pagination.
        :param sort: Sorting field.
        :param order: Sorting order.
        :param filter: Filter by field.
        :return: List of vendors.
        """
        params = {
            "offset": offset,
            "limit": limit,
            "sort": sort,
            "order": order,
            "filter": filter,
        }
        return await self.http_client.get(self.LIST_VENDORS_PATH, params=params)

    async def get_vendor(self, identifier: str) -> Dict[str, Any]:
        """
        Fetch a vendor by its identifier.
        :param identifier: The vendor's identifier.
        :return: Vendor details.
        """
        path = self.VENDOR_DETAIL_PATH.format(identifier=identifier)
        return await self.http_client.get(path)

    @validate_sorting(sort_pattern="^(name|created_at|updated_at)$")
    def list_vendors_sync(
        self,
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
        filter: str = "",
    ) -> List[Dict[str, Any]]:
        """
        Synchronous version of list_vendors.
        :param offset: Offset for pagination.
        :param limit: Limit for pagination.
        :param sort: Sorting field.
        :param order: Sorting order.
        :param filter: Filter by field.
        :return: List of vendors.
        """
        params = {
            "offset": offset,
            "limit": limit,
            "sort": sort,
            "order": order,
            "filter": filter,
        }
        return self.http_client.get_sync(self.LIST_VENDORS_PATH, params=params)

    def get_vendor_sync(self, identifier: str) -> Dict[str, Any]:
        """
        Synchronous version of get_vendor.
        :param identifier: The vendor's identifier.
        :return: Vendor details.
        """
        path = self.VENDOR_DETAIL_PATH.format(identifier=identifier)
        return self.http_client.get_sync(path)
