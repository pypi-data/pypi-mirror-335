"""
WireGuard Configuration API Client

A comprehensive client library and CLI tool for interacting with the
WireGuard Configuration Distribution API.
"""

__version__ = "0.1.5"

from wg_api_client.api import WireGuardAPI
from wg_api_client.config import ConfigManager
from wg_api_client.helper import WireGuardHelper

__all__ = ["WireGuardAPI", "ConfigManager", "WireGuardHelper"]
