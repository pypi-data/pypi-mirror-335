from typing import List, Dict, Any, Optional
from malloryai.sdk.api.v1.decorators.sorting import validate_sorting
from malloryai.sdk.api.v1.http_client import HttpClient


class ThreatActorsClient:
    """Client for managing threat actors."""

    LIST_THREAT_ACTORS_PATH = "/actors"
    THREAT_ACTOR_DETAIL_PATH = "/actors/{identifier}"
    LIST_THREAT_ACTORS_MENTIONED_PATH = "/mentions/actors"

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    @validate_sorting(sort_pattern="^(name|created_at|updated_at)$")
    async def list_threat_actors(
        self,
        filter: Optional[str] = "",
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """
        List threat actors.
        :param filter: Filter criteria.
        :param offset: Offset for pagination.
        :param limit: Limit for pagination.
        :param sort: Sorting field.
        :param order: Sorting order.
        :return: List of threat actors.
        """
        params = {
            "filter": filter,
            "offset": offset,
            "limit": limit,
            "sort": sort,
            "order": order,
        }
        return await self.http_client.get(self.LIST_THREAT_ACTORS_PATH, params=params)

    async def get_threat_actor(self, identifier: str) -> Dict[str, Any]:
        """
        Get a threat actor by identifier.
        :param identifier: The unique UUID or name of the threat actor to retrieve.
        :return: Threat actor details.
        """
        path = self.THREAT_ACTOR_DETAIL_PATH.format(identifier=identifier)
        return await self.http_client.get(path)

    @validate_sorting(
        sort_pattern="^(created_at|updated_at|published_at|collected_at)$"
    )
    async def list_threat_actors_mentioned(
        self,
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """
        List threat actors mentioned.
        :param offset: Offset for pagination.
        :param limit: Limit for pagination.
        :param sort: Sorting field.
        :param order: Sorting order.
        :return: List of threat actors mentioned.
        """
        params = {"offset": offset, "limit": limit, "sort": sort, "order": order}
        return await self.http_client.get(
            self.LIST_THREAT_ACTORS_MENTIONED_PATH, params=params
        )

    @validate_sorting(sort_pattern="^(name|created_at|updated_at)$")
    def list_threat_actors_sync(
        self,
        filter: Optional[str] = "",
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """
        Synchronous version of list_threat_actors.
        filter: Filter criteria.
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
        :return: List of threat actors.
        """
        params = {
            "filter": filter,
            "offset": offset,
            "limit": limit,
            "sort": sort,
            "order": order,
        }
        return self.http_client.get_sync(self.LIST_THREAT_ACTORS_PATH, params=params)

    def get_threat_actor_sync(self, identifier: str) -> Dict[str, Any]:
        """
        Synchronous version of get_threat_actor.
        :param identifier: The unique UUID or name of the threat actor to retrieve.
        :return: Threat actor details.
        """
        path = self.THREAT_ACTOR_DETAIL_PATH.format(identifier=identifier)
        return self.http_client.get_sync(path)

    @validate_sorting(
        sort_pattern="^(created_at|updated_at|published_at|collected_at)$"
    )
    def list_threat_actors_mentioned_sync(
        self,
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """
        Synchronous version of list_threat_actors_mentioned.
        :param offset: Offset for pagination.
        :param limit: Limit for pagination.
        :param sort: Sorting field.
        :param order: Sorting order.
        :return: List of threat actors mentioned.
        """
        params = {"offset": offset, "limit": limit, "sort": sort, "order": order}
        return self.http_client.get_sync(
            self.LIST_THREAT_ACTORS_MENTIONED_PATH, params=params
        )
