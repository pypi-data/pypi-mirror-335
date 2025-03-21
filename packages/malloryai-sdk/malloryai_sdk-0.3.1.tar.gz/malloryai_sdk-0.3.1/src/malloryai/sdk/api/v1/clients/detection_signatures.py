from typing import List, Dict, Any
from malloryai.sdk.api.v1.decorators.sorting import validate_sorting
from malloryai.sdk.api.v1.http_client import HttpClient


class DetectionSignaturesClient:
    """Client for managing detection signatures."""

    LIST_DETECTION_SIGNATURES_PATH = "/detection_signatures"
    DETECTION_SIGNATURE_DETAIL_PATH = "/detection_signatures/{identifier}"

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    @validate_sorting
    async def list_detection_signatures(
        self,
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """
        List detection signatures.
        :param offset: Offset for pagination.
        :param limit: Limit for pagination.
        :param sort: Sorting field.
        :param order: Sorting order.
        :return: List of detection signatures.
        """
        params = {"offset": offset, "limit": limit, "sort": sort, "order": order}
        return await self.http_client.get(
            self.LIST_DETECTION_SIGNATURES_PATH, params=params
        )

    async def get_detection_signature(self, identifier: str) -> Dict[str, Any]:
        """
        Get a detection signature.
        :param identifier: Detection signature identifier.
        :return: Detection signature.
        """
        path = self.DETECTION_SIGNATURE_DETAIL_PATH.format(identifier=identifier)
        return await self.http_client.get(path)

    def list_detection_signatures_sync(
        self,
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """
        Synchronous version of list_detection_signatures.
        :param offset: Offset for pagination.
        :param limit: Limit for pagination.
        :param sort: Sorting field.
        :param order: Sorting order.
        :return: List of detection signatures.
        """
        params = {"offset": offset, "limit": limit, "sort": sort, "order": order}
        return self.http_client.get_sync(
            self.LIST_DETECTION_SIGNATURES_PATH, params=params
        )

    def get_detection_signature_sync(self, identifier: str) -> Dict[str, Any]:
        """
        Synchronous version of get_detection_signature.
        :param identifier: Detection signature identifier.
        :return: Detection signature.
        """
        path = self.DETECTION_SIGNATURE_DETAIL_PATH.format(identifier=identifier)
        return self.http_client.get_sync(path)
