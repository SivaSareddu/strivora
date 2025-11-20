"""
Adaptive Login Integration for STRIVORA

Automatically handles complex login flows (like T-Mobile) using AI Vision
when testing domains that require authentication.
"""

from .domain_detector import should_use_adaptive_login, get_login_config
from .playwright_adapter import execute_adaptive_login_playwright
from .undetected_adapter import execute_adaptive_login_undetected

__all__ = [
    "should_use_adaptive_login",
    "get_login_config",
    "execute_adaptive_login_playwright",
    "execute_adaptive_login_undetected",
]

