from typing import List, Dict, Any
from malloryai.sdk.api.v1.http_client import HttpClient


class BulletinsClient:
    """Client for managing bulletins."""

    LIST_BULLETINS_PATH = "/bulletins"
    BULLETIN_DETAIL_PATH = "/bulletins/{identifier}"

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    async def list_bulletins(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List all bulletins.
        :param offset: Offset for pagination
        :param limit: Limit for pagination
        :return: List of bulletins
        """
        params = {"offset": offset, "limit": limit}
        return await self.http_client.get(self.LIST_BULLETINS_PATH, params=params)

    async def get_bulletin(self, identifier: str) -> Dict[str, Any]:
        """
        Get a bulletin by identifier.
        :param identifier: Identifier of the bulletin
        :return: Bulletin
        """
        path = self.BULLETIN_DETAIL_PATH.format(identifier=identifier)
        return await self.http_client.get(path)

    def list_bulletins_sync(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Synchronous version of list_bulletins.
        :param offset: Offset for pagination
        :param limit: Limit for pagination
        :return: List of bulletins
        """
        params = {"offset": offset, "limit": limit}
        return self.http_client.get_sync(self.LIST_BULLETINS_PATH, params=params)

    def get_bulletin_sync(self, identifier: str) -> Dict[str, Any]:
        """
        Synchronous version of get_bulletin.
        :param identifier: Identifier of the bulletin
        :return: Bulletin
        """
        path = self.BULLETIN_DETAIL_PATH.format(identifier=identifier)
        return self.http_client.get_sync(path)
