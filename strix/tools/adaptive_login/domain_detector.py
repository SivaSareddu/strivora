"""
Domain Detection Module

Detects when a domain requires adaptive login and provides configuration.
"""
import os
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Domain configurations for adaptive login
ADAPTIVE_LOGIN_DOMAINS = {
    "my.t-mobile.com": {
        "enabled": True,
        "email_env": "TMO_LOGIN",
        "password_env": "TMO_PASSWORD",
        "login_url": "https://account.t-mobile.com/signin/v2/",
        "description": "T-Mobile multi-step login with MFA support",
    },
    "account.t-mobile.com": {
        "enabled": True,
        "email_env": "TMO_LOGIN",
        "password_env": "TMO_PASSWORD",
        "login_url": "https://account.t-mobile.com/signin/v2/",
        "description": "T-Mobile account login",
    },
    "www.t-mobile.com": {
        "enabled": True,
        "email_env": "TMO_LOGIN",
        "password_env": "TMO_PASSWORD",
        "login_url": "https://account.t-mobile.com/signin/v2/",
        "description": "T-Mobile website login",
    },
}


def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove port if present
        if ":" in domain:
            domain = domain.split(":")[0]
        return domain
    except Exception as e:
        logger.warning(f"Failed to parse URL {url}: {e}")
        return ""


def should_use_adaptive_login(url: str) -> bool:
    """
    Check if the URL domain requires adaptive login.
    
    Args:
        url: The URL to check
        
    Returns:
        True if adaptive login should be used for this domain
    """
    domain = extract_domain(url)
    
    # Check exact domain match
    if domain in ADAPTIVE_LOGIN_DOMAINS:
        config = ADAPTIVE_LOGIN_DOMAINS[domain]
        if config.get("enabled", False):
            logger.info(f"✅ Adaptive login enabled for domain: {domain}")
            return True
    
    # Check subdomain matches (e.g., *.t-mobile.com)
    for configured_domain, config in ADAPTIVE_LOGIN_DOMAINS.items():
        if config.get("enabled", False):
            # Check if domain ends with configured domain (subdomain match)
            if domain.endswith("." + configured_domain) or domain == configured_domain:
                logger.info(f"✅ Adaptive login enabled for domain: {domain} (matches {configured_domain})")
                return True
    
    return False


def get_login_config(url: str) -> Optional[Dict[str, Any]]:
    """
    Get login configuration for a domain.
    
    Args:
        url: The URL to get config for
        
    Returns:
        Configuration dict with email, password, login_url, etc. or None
    """
    domain = extract_domain(url)
    
    # Find matching domain config
    config = None
    for configured_domain, domain_config in ADAPTIVE_LOGIN_DOMAINS.items():
        if domain == configured_domain or domain.endswith("." + configured_domain):
            config = domain_config.copy()
            break
    
    if not config or not config.get("enabled", False):
        return None
    
    # Get credentials from environment
    email = os.getenv(config.get("email_env", ""))
    password = os.getenv(config.get("password_env", ""))
    
    if not email or not password:
        logger.warning(
            f"⚠️  Adaptive login configured for {domain} but credentials not found in environment. "
            f"Set {config.get('email_env')} and {config.get('password_env')}"
        )
        return None
    
    return {
        "domain": domain,
        "email": email,
        "password": password,
        "login_url": config.get("login_url", url),
        "description": config.get("description", ""),
    }

