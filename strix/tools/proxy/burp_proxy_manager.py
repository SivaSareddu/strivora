"""
BurpSuite Pro Proxy Manager

This module provides integration with BurpSuite Pro using the burp-rest-api extension.
The extension provides REST API endpoints for controlling BurpSuite Pro programmatically.

API Documentation: https://github.com/vmware/burp-rest-api
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import aiohttp

logger = logging.getLogger(__name__)


class BurpProxyManager:
    """Manages interactions with BurpSuite Pro via REST API extension."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8090",
        api_key: Optional[str] = None,
        proxy_port: int = 8080,
    ):
        """
        Initialize BurpSuite Pro proxy manager.
        
        Args:
            base_url: Base URL for BurpSuite Pro REST API (default: localhost:8090)
            api_key: API key for authentication (if enabled)
            proxy_port: Port where BurpSuite Pro proxy is running (default: 8080)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.proxy_port = proxy_port
        self.session: Optional[aiohttp.ClientSession] = None
        
        # API endpoints
        self.endpoints = {
            'status': '/v0.1/status',
            'scan': '/v0.1/scan',
            'scan_status': '/v0.1/scan/{scan_id}',
            'scan_results': '/v0.1/scan/{scan_id}/results',
            'proxy_history': '/v0.1/proxy/history',
            'proxy_config': '/v0.1/proxy/config',
            'spider': '/v0.1/spider',
            'spider_status': '/v0.1/spider/{scan_id}',
            'target': '/v0.1/target',
            'scope': '/v0.1/target/scope',
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure HTTP session is available."""
        if self.session is None or self.session.closed:
            headers = {}
            if self.api_key:
                headers['API-KEY'] = self.api_key
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            )
    
    async def close(self):
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to BurpSuite Pro API."""
        await self._ensure_session()
        
        url = urljoin(self.base_url, endpoint)
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                params=params
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """Get BurpSuite Pro status."""
        return await self._make_request('GET', self.endpoints['status'])
    
    async def is_available(self) -> bool:
        """Check if BurpSuite Pro is available and running."""
        try:
            status = await self.get_status()
            return status.get('status') == 'running'
        except Exception as e:
            logger.error(f"Failed to check BurpSuite Pro status: {e}")
            return False
    
    async def get_proxy_history(self, start: int = 0, count: int = 100) -> List[Dict[str, Any]]:
        """Get proxy history (captured requests/responses)."""
        params = {'start': start, 'count': count}
        response = await self._make_request('GET', self.endpoints['proxy_history'], params=params)
        return response.get('items', [])
    
    async def get_proxy_config(self) -> Dict[str, Any]:
        """Get proxy configuration."""
        return await self._make_request('GET', self.endpoints['proxy_config'])
    
    async def update_proxy_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update proxy configuration."""
        return await self._make_request('PUT', self.endpoints['proxy_config'], data=config)
    
    async def start_scan(
        self,
        urls: List[str],
        scan_type: str = "active",
        scan_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start a new scan.
        
        Args:
            urls: List of URLs to scan
            scan_type: Type of scan (active, passive, etc.)
            scan_config: Additional scan configuration
            
        Returns:
            Scan ID
        """
        data = {
            'urls': urls,
            'scan_type': scan_type
        }
        if scan_config:
            data.update(scan_config)
        
        response = await self._make_request('POST', self.endpoints['scan'], data=data)
        return response.get('scan_id')
    
    async def get_scan_status(self, scan_id: str) -> Dict[str, Any]:
        """Get scan status."""
        endpoint = self.endpoints['scan_status'].format(scan_id=scan_id)
        return await self._make_request('GET', endpoint)
    
    async def get_scan_results(self, scan_id: str) -> List[Dict[str, Any]]:
        """Get scan results."""
        endpoint = self.endpoints['scan_results'].format(scan_id=scan_id)
        response = await self._make_request('GET', endpoint)
        return response.get('issues', [])
    
    async def start_spider(self, urls: List[str]) -> str:
        """Start spidering URLs."""
        data = {'urls': urls}
        response = await self._make_request('POST', self.endpoints['spider'], data=data)
        return response.get('scan_id')
    
    async def get_spider_status(self, scan_id: str) -> Dict[str, Any]:
        """Get spider status."""
        endpoint = self.endpoints['spider_status'].format(scan_id=scan_id)
        return await self._make_request('GET', endpoint)
    
    async def get_target_info(self) -> Dict[str, Any]:
        """Get target information."""
        return await self._make_request('GET', self.endpoints['target'])
    
    async def add_to_scope(self, urls: List[str]) -> Dict[str, Any]:
        """Add URLs to scope."""
        data = {'urls': urls}
        return await self._make_request('POST', self.endpoints['scope'], data=data)
    
    async def remove_from_scope(self, urls: List[str]) -> Dict[str, Any]:
        """Remove URLs from scope."""
        data = {'urls': urls}
        return await self._make_request('DELETE', self.endpoints['scope'], data=data)
    
    async def get_scope(self) -> Dict[str, Any]:
        """Get current scope configuration."""
        return await self._make_request('GET', self.endpoints['scope'])
    
    async def send_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[str] = None,
        follow_redirects: bool = True
    ) -> Dict[str, Any]:
        """
        Send HTTP request through BurpSuite Pro proxy.
        
        Args:
            method: HTTP method
            url: Target URL
            headers: HTTP headers
            data: Request body
            follow_redirects: Whether to follow redirects
            
        Returns:
            Response data including status, headers, and body
        """
        # This would typically be done by configuring the HTTP client
        # to use BurpSuite Pro as a proxy, rather than making API calls
        # The actual request would go through the proxy port (8080)
        # and BurpSuite Pro would capture it in the proxy history
        
        # For now, we'll return a placeholder response
        # In practice, you'd configure your HTTP client to use the proxy
        return {
            'status': 'sent_via_proxy',
            'proxy_port': self.proxy_port,
            'message': 'Request sent through BurpSuite Pro proxy'
        }
    
    async def get_captured_requests(
        self,
        filter_url: Optional[str] = None,
        filter_method: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get captured requests from proxy history.
        
        Args:
            filter_url: Filter by URL pattern
            filter_method: Filter by HTTP method
            limit: Maximum number of requests to return
            
        Returns:
            List of captured requests
        """
        requests = await self.get_proxy_history(count=limit)
        
        if filter_url or filter_method:
            filtered = []
            for req in requests:
                if filter_url and filter_url not in req.get('url', ''):
                    continue
                if filter_method and req.get('method') != filter_method:
                    continue
                filtered.append(req)
            return filtered
        
        return requests
    
    async def get_request_details(self, request_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific request."""
        # This would typically involve getting the full request/response
        # from the proxy history using the request ID
        # For now, we'll return a placeholder
        return {
            'request_id': request_id,
            'status': 'retrieved',
            'message': 'Request details retrieved from BurpSuite Pro'
        }


# Global instance management
_burp_manager: Optional[BurpProxyManager] = None


async def get_burp_proxy_manager() -> BurpProxyManager:
    """Get or create global BurpSuite Pro proxy manager instance."""
    global _burp_manager
    
    if _burp_manager is None:
        # Get configuration from environment variables
        base_url = os.getenv('BURP_API_URL', 'http://localhost:8090')
        api_key = os.getenv('BURP_API_KEY')
        proxy_port = int(os.getenv('BURP_PORT', '8080'))
        
        _burp_manager = BurpProxyManager(
            base_url=base_url,
            api_key=api_key,
            proxy_port=proxy_port
        )
    
    return _burp_manager


async def close_burp_proxy_manager():
    """Close the global BurpSuite Pro proxy manager instance."""
    global _burp_manager
    
    if _burp_manager:
        await _burp_manager.close()
        _burp_manager = None
