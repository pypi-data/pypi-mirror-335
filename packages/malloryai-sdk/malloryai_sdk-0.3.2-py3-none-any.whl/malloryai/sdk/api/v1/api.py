from typing import Optional
import logging

from malloryai.sdk.api.v1.clients import (
    SourcesClient,
    ReferencesClient,
    ContentChunksClient,
    ThreatActorsClient,
    VulnerabilitiesClient,
    ExploitsClient,
    ExploitationsClient,
    BulletinsClient,
    DetectionSignaturesClient,
    ProductsClient,
    VendorsClient,
)
from malloryai.sdk.api.v1.http_client import HttpClient


class MalloryIntelligenceClient:
    """Main SDK class to interact with Mallory Intelligence API."""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the Mallory API client.
        :param api_key:
        :param base_url:
        :param logger:
        """
        self.http_client = HttpClient(api_key=api_key, base_url=base_url, logger=logger)
        self.sources = SourcesClient(self.http_client)
        self.references = ReferencesClient(self.http_client)
        self.content_chunks = ContentChunksClient(self.http_client)
        self.threat_actors = ThreatActorsClient(self.http_client)
        self.vulnerabilities = VulnerabilitiesClient(self.http_client)
        self.exploits = ExploitsClient(self.http_client)
        self.exploitations = ExploitationsClient(self.http_client)
        self.bulletins = BulletinsClient(self.http_client)
        self.detection_signatures = DetectionSignaturesClient(self.http_client)
        self.products = ProductsClient(self.http_client)
        self.vendors = VendorsClient(self.http_client)
