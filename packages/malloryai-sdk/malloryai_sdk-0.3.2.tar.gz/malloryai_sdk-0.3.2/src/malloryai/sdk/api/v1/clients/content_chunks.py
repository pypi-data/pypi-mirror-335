from typing import List, Dict, Any, Optional
from malloryai.sdk.api.v1.http_client import HttpClient


class ContentChunksClient:
    """Client for managing content chunks."""

    LIST_CONTENT_CHUNKS_PATH = "/content_chunks"
    CONTENT_CHUNK_DETAIL_PATH = "/content_chunks/{identifier}"

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    async def list_content_chunks(
        self, filter: Optional[str] = "", offset: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List content chunks.
        :param filter: Filter content chunks by available filters.
        :param offset: Offset for pagination.
        :param limit: Limit for pagination.
        :return: List of content chunks.
        """
        params = {"filter": filter, "offset": offset, "limit": limit}
        return await self.http_client.get(self.LIST_CONTENT_CHUNKS_PATH, params=params)

    async def get_content_chunk(self, identifier: str) -> Dict[str, Any]:
        """
        Get a content chunk by identifier.
        :param identifier: Identifier of the content chunk.
        :return: Content chunk details.
        """
        path = self.CONTENT_CHUNK_DETAIL_PATH.format(identifier=identifier)
        return await self.http_client.get(path)

    def list_content_chunks_sync(
        self, filter: Optional[str] = "", offset: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Synchronous version of list_content_chunks.
        :param filter: Filter content chunks by available filters.
        :param offset: Offset for pagination.
        :param limit: Limit for pagination.
        :return: List of content chunks.
        """
        params = {"filter": filter, "offset": offset, "limit": limit}
        return self.http_client.get_sync(self.LIST_CONTENT_CHUNKS_PATH, params=params)

    def get_content_chunk_sync(self, identifier: str) -> Dict[str, Any]:
        """
        Synchronous version of get_content_chunk.
        :param identifier: Identifier of the content chunk.
        :return: Content chunk details.
        """
        path = self.CONTENT_CHUNK_DETAIL_PATH.format(identifier=identifier)
        return self.http_client.get_sync(path)
