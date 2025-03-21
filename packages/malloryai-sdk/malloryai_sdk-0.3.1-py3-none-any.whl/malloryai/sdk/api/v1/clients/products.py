from typing import List, Dict, Any, Optional
from malloryai.sdk.api.v1.decorators.sorting import validate_sorting
from malloryai.sdk.api.v1.http_client import HttpClient


class ProductsClient:
    """Client for managing products."""

    LIST_PRODUCTS_PATH = "/products"
    PRODUCT_DETAIL_PATH = "/products/{identifier}"
    SEARCH_PRODUCTS_PATH = "/products/search"

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    @validate_sorting(sort_pattern="^(name|created_at|updated_at)$")
    async def list_products(
        self,
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
        filter: str = "",
    ) -> List[Dict[str, Any]]:
        """
        List all products.
        :param offset: Offset for pagination.
        :param limit: Limit for pagination.
        :param sort: Sorting field.
        :param order: Sorting order.
        :param filter: Filter by field.
        :return: List of products.
        """
        params = {
            "offset": offset,
            "limit": limit,
            "sort": sort,
            "order": order,
            "filter": filter,
        }
        return await self.http_client.get(self.LIST_PRODUCTS_PATH, params=params)

    async def get_product(self, identifier: str) -> Dict[str, Any]:
        """
        Fetch a product by its identifier.
        :param identifier: The unique UUID of the technology product to retrieve.
        :return: The product.
        """
        path = self.PRODUCT_DETAIL_PATH.format(identifier=identifier)
        return await self.http_client.get(path)

    @validate_sorting(sort_pattern="^(name|created_at|updated_at)$")
    async def search_products(
        self,
        search_type: Optional[str] = "",
        product: Optional[str] = "",
        vendor: Optional[str] = "",
        cpe: Optional[str] = "",
        type: Optional[str] = "",
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """
        Search for products.
        :param search_type: Options: 'standard' (default), 'did_you_mean'.
        :param product: The product name to search for.
        :param vendor: The vendor name to search for.
        :param cpe: The CPE to search for.
        :param type: The type of the product (e.g., application (default), operating system).
        :param offset: Offset for pagination.
        :param limit: Limit for pagination.
        :param sort: Sorting field.
        :param order: Sorting order.
        :return: List of products.
        """
        payload = {
            "vendor": vendor,
            "product": product,
            "cpe": cpe,
            "type": type,
            "search_type": search_type,
        }
        params = {"offset": offset, "limit": limit, "sort": sort, "order": order}
        return await self.http_client.post(
            self.SEARCH_PRODUCTS_PATH, json=payload, params=params
        )

    def list_products_sync(
        self,
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
        filter: str = "",
    ) -> List[Dict[str, Any]]:
        """
        Synchronous version of list_products.
        """
        params = {
            "offset": offset,
            "limit": limit,
            "sort": sort,
            "order": order,
            "filter": filter,
        }
        return self.http_client.get_sync(self.LIST_PRODUCTS_PATH, params=params)

    def get_product_sync(self, identifier: str) -> Dict[str, Any]:
        """
        Synchronous version of get_product.
        """
        path = self.PRODUCT_DETAIL_PATH.format(identifier=identifier)
        return self.http_client.get_sync(path)

    def search_products_sync(
        self,
        search_type: Optional[str] = "",
        product: Optional[str] = "",
        vendor: Optional[str] = "",
        cpe: Optional[str] = "",
        type: Optional[str] = "",
        offset: int = 0,
        limit: int = 100,
        sort: str = "created_at",
        order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """
        Synchronous version of search_products.
        """
        payload = {
            "vendor": vendor,
            "product": product,
            "cpe": cpe,
            "type": type,
            "search_type": search_type,
        }
        params = {"offset": offset, "limit": limit, "sort": sort, "order": order}
        return self.http_client.post_sync(
            self.SEARCH_PRODUCTS_PATH, json=payload, params=params
        )
