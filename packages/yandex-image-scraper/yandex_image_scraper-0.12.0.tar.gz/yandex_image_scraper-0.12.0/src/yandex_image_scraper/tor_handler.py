#!/usr/bin/env python3
"""
Tor handler module for Yandex Image Scraper
Provides functionality to route traffic through Tor's SOCKS proxy
"""

import socket
import aiohttp
from typing import Dict, Any, Optional, Tuple

# Default Tor SOCKS proxy settings
TOR_PROXY = "socks5://127.0.0.1:9050"

def is_tor_running() -> bool:
    """
    Check if Tor SOCKS proxy is running by attempting to connect to it
    
    Returns:
        bool: True if Tor is running, False otherwise
    """
    try:
        # Extract host and port from the proxy string
        proxy_parts = TOR_PROXY.split("://")[1].split(":")
        host = proxy_parts[0]
        port = int(proxy_parts[1])
        
        # Try to connect to the Tor SOCKS proxy
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(3)
            result = sock.connect_ex((host, port))
            return result == 0
    except Exception:
        return False

async def check_tor_connection() -> Tuple[bool, Optional[str]]:
    """
    Checks if the Tor connection is working by making a request to the Tor check service
    
    Returns:
        Tuple[bool, Optional[str]]: (is_connected, ip_address)
    """
    try:
        # Configure aiohttp to use the Tor SOCKS proxy
        proxy_connector = aiohttp.TCPConnector(
            ssl=False,
            force_close=True,
            enable_cleanup_closed=True
        )
        
        async with aiohttp.ClientSession(connector=proxy_connector) as session:
            # Make request through Tor to check.torproject.org
            async with session.get(
                "https://check.torproject.org/api/ip",
                proxy=TOR_PROXY,
                timeout=30
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("IsTor", False), data.get("IP")
                return False, None
    except Exception:
        return False, None

def get_tor_browser_config() -> Dict[str, Any]:
    """
    Get browser configuration for using Tor
    
    Returns:
        Dict[str, Any]: Browser configuration dictionary for AsyncCamoufox
    """
    return {
        "proxy": {
            "server": TOR_PROXY
        }
    }
