#!/usr/bin/env python3
"""
Test script to verify adaptive login integration with STRIVORA.

This script tests:
1. Domain detection for T-Mobile domains
2. Playwright adapter integration
3. Undetected-chromedriver adapter (optional)
"""
import asyncio
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Add STRIVORA to path
strivora_path = Path(__file__).parent
sys.path.insert(0, str(strivora_path))

# Import STRIVORA modules
try:
    from strix.tools.adaptive_login import (
        should_use_adaptive_login,
        get_login_config,
        execute_adaptive_login_playwright,
        execute_adaptive_login_undetected,
    )
    from strix.tools.browser.browser_instance import BrowserInstance
except ImportError as e:
    logger.error(f"❌ Failed to import STRIVORA modules: {e}")
    sys.exit(1)


def test_domain_detection():
    """Test domain detection logic."""
    logger.info("=" * 60)
    logger.info("TEST 1: Domain Detection")
    logger.info("=" * 60)
    
    test_urls = [
        "https://my.t-mobile.com/dashboard",
        "https://account.t-mobile.com/signin/v2/",
        "https://www.t-mobile.com/account",
        "https://example.com/login",
    ]
    
    for url in test_urls:
        should_use = should_use_adaptive_login(url)
        config = get_login_config(url)
        logger.info(f"URL: {url}")
        logger.info(f"  Should use adaptive login: {should_use}")
        if config:
            logger.info(f"  Config found: {config['domain']}")
            logger.info(f"  Email: {config['email'][:10]}...")
        else:
            logger.info(f"  Config: None")
        logger.info("")


async def test_playwright_adapter():
    """Test Playwright adapter integration."""
    logger.info("=" * 60)
    logger.info("TEST 2: Playwright Adapter Integration")
    logger.info("=" * 60)
    
    # Check credentials
    email = os.getenv("TMO_LOGIN")
    password = os.getenv("TMO_PASSWORD")
    
    if not email or not password:
        logger.warning("⚠️  TMO_LOGIN and TMO_PASSWORD not set in environment")
        logger.warning("   Skipping Playwright adapter test")
        return
    
    try:
        browser_instance = BrowserInstance()
        logger.info("✅ Browser instance created")
        
        # Launch browser
        result = browser_instance.launch()
        logger.info(f"✅ Browser launched: {result.get('message')}")
        
        # Test navigation to T-Mobile login page
        login_url = "https://account.t-mobile.com/signin/v2/"
        logger.info(f"🌐 Navigating to: {login_url}")
        
        result = browser_instance.goto(login_url)
        logger.info(f"✅ Navigation result: {result.get('message')}")
        logger.info(f"   URL: {result.get('url')}")
        
        # Check if adaptive login was triggered
        if "adaptive" in str(result).lower() or "login" in str(result).lower():
            logger.info("✅ Adaptive login appears to have been triggered")
        else:
            logger.info("ℹ️  Normal navigation (adaptive login may have run silently)")
        
        # Close browser
        browser_instance.close()
        logger.info("✅ Browser closed")
        
    except Exception as e:
        logger.error(f"❌ Playwright adapter test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())


async def test_undetected_adapter():
    """Test undetected-chromedriver adapter."""
    logger.info("=" * 60)
    logger.info("TEST 3: Undetected Chrome Adapter (Optional)")
    logger.info("=" * 60)
    
    email = os.getenv("TMO_LOGIN")
    password = os.getenv("TMO_PASSWORD")
    
    if not email or not password:
        logger.warning("⚠️  TMO_LOGIN and TMO_PASSWORD not set")
        logger.warning("   Skipping undetected adapter test")
        return
    
    try:
        login_url = "https://account.t-mobile.com/signin/v2/"
        logger.info(f"🌐 Testing undetected Chrome adapter with: {login_url}")
        
        result = await execute_adaptive_login_undetected(
            email=email,
            password=password,
            login_url=login_url,
            headless=False,  # Set to True for headless mode
        )
        
        if result.get("success"):
            logger.info(f"✅ Undetected adapter test successful: {result.get('stage')}")
        else:
            logger.warning(f"⚠️  Undetected adapter test failed: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ Undetected adapter test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())


async def main():
    """Run all tests."""
    logger.info("🚀 Starting Adaptive Login Integration Tests")
    logger.info("")
    
    # Test 1: Domain detection
    test_domain_detection()
    
    # Test 2: Playwright adapter
    await test_playwright_adapter()
    
    # Test 3: Undetected adapter (optional)
    logger.info("")
    response = input("Run undetected-chromedriver test? (y/n): ").strip().lower()
    if response == "y":
        await test_undetected_adapter()
    else:
        logger.info("⏭️  Skipping undetected adapter test")
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("✅ All tests completed")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

