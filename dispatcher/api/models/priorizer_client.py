"""
HTTP client to communicate with the priorizer service.
"""

import httpx
import logging
from typing import List, Optional
from models.payload import BaseAssetModel

logger = logging.getLogger(__name__)


class PriorizerClient:
    """HTTP client to communicate with the priorizer service."""
    
    def __init__(self, base_url: str = "http://priorizer-api:8082"):
        """
        Initializes the priorizer client.
        
        Args:
            base_url: Base URL of the priorizer service
        """
        self.base_url = base_url.rstrip('/')
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Returns or creates an asynchronous HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
        return self._client
    
    async def close(self):
        """Closes the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def get_ranking(self) -> List[BaseAssetModel]:
        """
        Retrieves the ranking of assets from the priorizer.
        
        Returns:
            List of assets ranked by priority
            
        Raises:
            httpx.HTTPError: In case of HTTP error
            ValueError: In case of invalid response
        """
        client = await self._get_client()
        
        try:
            logger.info(f"Retrieving ranking from {self.base_url}/ranking")
            response = await client.post(f"{self.base_url}/ranking")
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Ranking received: {len(data.get('asset', []))} assets")
            
            # Data to BaseAssetModel conversion
            assets = []
            for asset_data in data.get('asset', []):
                try:
                    asset = BaseAssetModel(**asset_data)
                    assets.append(asset)
                except Exception as e:
                    logger.warning(f"Invalid asset ignored: {asset_data}, error: {e}")
                    continue
            
            return assets
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from priorizer: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Connection error to priorizer: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error when retrieving ranking: {e}")
            raise
