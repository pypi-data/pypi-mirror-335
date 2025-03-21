from typing import List, Dict, Any
from malloryai.sdk.api.v1.http_client import HttpClient


class SourcesClient:
    """Client for managing sources."""

    LIST_SOURCES_PATH = "/sources"

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    async def list_sources(self) -> List[Dict[str, Any]]:
        """
        List all sources.
        :return: List of sources.
        """
        return await self.http_client.get(self.LIST_SOURCES_PATH)

    def list_sources_sync(self) -> List[Dict[str, Any]]:
        """
        Synchronous version of list_sources.
        :return: List of sources.
        """
        return self.http_client.get_sync(self.LIST_SOURCES_PATH)
