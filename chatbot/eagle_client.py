"""
Eagle API Client for Django Backend
Fetches property data from Eagle API via Next.js proxy
"""

import os
import requests
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EagleAPIClient:
    """
    Client for fetching Eagle properties via Next.js proxy.
    Uses the existing Next.js API routes that handle authentication.
    """

    def __init__(self, frontend_url: Optional[str] = None):
        """
        Initialize Eagle API client.
        
        Args:
            frontend_url: Base URL of Next.js frontend
                         Defaults to FRONTEND_URL env var or localhost:3000
        """
        if frontend_url is None:
            # Try environment variable first, then default to localhost
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        
        self.frontend_url = frontend_url.rstrip('/')
        self.timeout = 45
        logger.info(f"[Eagle Client] Initialized with frontend URL: {self.frontend_url}")

    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make HTTP request to Next.js proxy.
        
        Args:
            endpoint: API endpoint path (e.g., '/api/eagle/properties')
            params: Query parameters
            
        Returns:
            JSON response data
            
        Raises:
            Exception: If request fails
        """
        url = f"{self.frontend_url}{endpoint}"
        
        try:
            logger.info(f"[Eagle Client] Requesting: {url} with params: {params}")
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code != 200:
                logger.error(f"[Eagle Client] Request failed: {response.status_code} - {response.text}")
                raise Exception(f"Eagle API request failed: {response.status_code}")
            
            data = response.json()
            logger.info(f"[Eagle Client] Success: received {len(data.get('properties', []))} properties")
            return data
            
        except requests.RequestException as e:
            logger.error(f"[Eagle Client] Request exception: {str(e)}")
            raise Exception(f"Failed to fetch from Eagle API: {str(e)}")

    def search_properties(
        self,
        search_term: Optional[str] = None,
        limit: int = 20,
        status: Optional[str] = None,
        property_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search properties from Eagle API.
        
        Args:
            search_term: Search query (searches address, headline, description)
            limit: Maximum number of results
            status: Property status filter (e.g., 'ACTIVE', 'SOLD')
            property_type: Property type filter (e.g., 'HOUSE', 'APARTMENT')
            
        Returns:
            List of property dictionaries
        """
        params = {'limit': limit}
        
        if search_term:
            params['search'] = search_term
        if status:
            params['status'] = status
        if property_type:
            params['propertyType'] = property_type
        
        try:
            data = self._make_request('/api/eagle/properties', params)
            return data.get('properties', [])
        except Exception as e:
            logger.error(f"[Eagle Client] Search failed: {str(e)}")
            return []

    def get_property_by_id(self, property_id: str) -> Optional[Dict[str, Any]]:
        """
        Get single property by ID from Eagle API.
        
        Args:
            property_id: Eagle property ID
            
        Returns:
            Property dictionary or None if not found
        """
        try:
            data = self._make_request(f'/api/eagle/properties/{property_id}')
            return data.get('property')
        except Exception as e:
            logger.error(f"[Eagle Client] Get property failed: {str(e)}")
            return None

    def get_featured_properties(self, limit: int = 8) -> List[Dict[str, Any]]:
        """
        Get featured/active properties from Eagle API.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of property dictionaries
        """
        # Search with empty search_term to get all ACTIVE properties
        return self.search_properties(search_term="", limit=limit, status='ACTIVE')

    def test_connection(self) -> Dict[str, Any]:
        """
        Test Eagle API connection via Next.js proxy.
        
        Returns:
            Test result dictionary with success status
        """
        try:
            data = self._make_request('/api/eagle/test-auth')
            return data
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
_eagle_client = None


def get_eagle_client() -> EagleAPIClient:
    """
    Get singleton Eagle API client instance.
    
    Returns:
        EagleAPIClient instance
    """
    global _eagle_client
    if _eagle_client is None:
        _eagle_client = EagleAPIClient()
    return _eagle_client
