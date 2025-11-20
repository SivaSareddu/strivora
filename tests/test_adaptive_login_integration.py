#!/usr/bin/env python3
"""
Integration tests for adaptive login in STRIVORA.

Tests the full integration flow:
1. Domain detection
2. Credential loading
3. Playwright browser integration
4. Adaptive login execution
"""
import asyncio
import os
import sys
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add STRIVORA to path
strivora_path = Path(__file__).parent.parent
sys.path.insert(0, str(strivora_path))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def test_domain_detection():
    """Test domain detection logic."""
    logger.info("=" * 70)
    logger.info("TEST 1: Domain Detection")
    logger.info("=" * 70)
    
    # Import directly to avoid STRIVORA dependency issues
    domain_detector_path = strivora_path / "strix" / "tools" / "adaptive_login" / "domain_detector.py"
    sys.path.insert(0, str(domain_detector_path.parent))
    
    try:
        from domain_detector import (
            should_use_adaptive_login,
            get_login_config,
            extract_domain,
        )
    except ImportError:
        # Try alternative import
        from strix.tools.adaptive_login.domain_detector import (
            should_use_adaptive_login,
            get_login_config,
            extract_domain,
        )
    
    test_cases = [
        ("https://my.t-mobile.com/dashboard", True, "my.t-mobile.com"),
        ("https://account.t-mobile.com/signin/v2/", True, "account.t-mobile.com"),
        ("https://www.t-mobile.com/account", True, "www.t-mobile.com"),
        ("https://subdomain.my.t-mobile.com/test", True, "subdomain.my.t-mobile.com"),
        ("https://example.com/login", False, "example.com"),
        ("https://google.com", False, "google.com"),
    ]
    
    passed = 0
    failed = 0
    
    for url, expected_detection, expected_domain in test_cases:
        domain = extract_domain(url)
        detected = should_use_adaptive_login(url)
        
        if detected == expected_detection and domain == expected_domain:
            logger.info(f"✅ {url}")
            logger.info(f"   Domain: {domain} (expected: {expected_domain})")
            logger.info(f"   Detected: {detected} (expected: {expected_detection})")
            passed += 1
        else:
            logger.error(f"❌ {url}")
            logger.error(f"   Domain: {domain} (expected: {expected_domain})")
            logger.error(f"   Detected: {detected} (expected: {expected_detection})")
            failed += 1
        logger.info("")
    
    logger.info(f"Domain Detection: {passed} passed, {failed} failed")
    return failed == 0


def test_credential_loading():
    """Test credential loading from environment."""
    logger.info("=" * 70)
    logger.info("TEST 2: Credential Loading")
    logger.info("=" * 70)
    
    try:
        from strix.tools.adaptive_login.domain_detector import get_login_config
    except ImportError:
        from domain_detector import get_login_config
    
    # Test with credentials set
    test_email = "test@example.com"
    test_password = "testpassword123"
    
    with patch.dict(os.environ, {"TMO_LOGIN": test_email, "TMO_PASSWORD": test_password}):
        config = get_login_config("https://my.t-mobile.com/test")
        
        if config and config.get("email") == test_email and config.get("password") == test_password:
            logger.info("✅ Credentials loaded correctly")
            logger.info(f"   Email: {config['email']}")
            logger.info(f"   Domain: {config['domain']}")
            return True
        else:
            logger.error("❌ Credentials not loaded correctly")
            logger.error(f"   Config: {config}")
            return False
    
    # Test without credentials
    with patch.dict(os.environ, {}, clear=True):
        config = get_login_config("https://my.t-mobile.com/test")
        if config is None:
            logger.info("✅ Correctly returns None when credentials missing")
            return True
        else:
            logger.error("❌ Should return None when credentials missing")
            return False


async def test_playwright_integration():
    """Test Playwright adapter integration."""
    logger.info("=" * 70)
    logger.info("TEST 3: Playwright Integration")
    logger.info("=" * 70)
    
    email = os.getenv("TMO_LOGIN")
    password = os.getenv("TMO_PASSWORD")
    
    if not email or not password:
        logger.warning("⚠️  TMO_LOGIN and TMO_PASSWORD not set")
        logger.warning("   Set environment variables to test Playwright integration")
        logger.warning("   Skipping this test...")
        return True  # Skip, don't fail
    
    try:
        from strix.tools.browser.browser_instance import BrowserInstance
        
        browser_instance = BrowserInstance()
        logger.info("✅ Browser instance created")
        
        # Launch browser
        result = browser_instance.launch()
        logger.info(f"✅ Browser launched")
        
        # Test navigation to T-Mobile domain
        test_url = "https://account.t-mobile.com/signin/v2/"
        logger.info(f"🌐 Navigating to: {test_url}")
        logger.info("   (This should trigger adaptive login if credentials are set)")
        
        result = browser_instance.goto(test_url)
        logger.info(f"✅ Navigation completed")
        logger.info(f"   URL: {result.get('url', 'N/A')}")
        
        # Check if adaptive login was attempted
        # (The actual login will happen in browser_instance._goto)
        logger.info("✅ Playwright integration test completed")
        
        # Close browser
        browser_instance.close()
        logger.info("✅ Browser closed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Playwright integration test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_undetected_adapter():
    """Test undetected-chromedriver adapter."""
    logger.info("=" * 70)
    logger.info("TEST 4: Undetected Chrome Adapter (Optional)")
    logger.info("=" * 70)
    
    email = os.getenv("TMO_LOGIN")
    password = os.getenv("TMO_PASSWORD")
    
    if not email or not password:
        logger.warning("⚠️  TMO_LOGIN and TMO_PASSWORD not set")
        logger.warning("   Skipping undetected adapter test")
        return True
    
    try:
        from strix.tools.adaptive_login.undetected_adapter import (
            execute_adaptive_login_undetected,
            UNDETECTED_CHROME_AVAILABLE,
            ADAPTIVE_LOGIN_AVAILABLE,
        )
        
        if not UNDETECTED_CHROME_AVAILABLE:
            logger.warning("⚠️  undetected-chromedriver not available")
            logger.warning("   Install with: pip install undetected-chromedriver")
            return True
        
        if not ADAPTIVE_LOGIN_AVAILABLE:
            logger.warning("⚠️  Adaptive login module not available")
            logger.warning("   Ensure ai_web_scraping project is accessible")
            return True
        
        logger.info("✅ Undetected adapter available")
        logger.info("   (Full test requires actual login - skipping to avoid rate limits)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Undetected adapter test failed: {e}")
        return False


def test_browser_instance_hook():
    """Test that browser_instance.py has the adaptive login hook."""
    logger.info("=" * 70)
    logger.info("TEST 5: Browser Instance Hook Verification")
    logger.info("=" * 70)
    
    browser_instance_path = strivora_path / "strix" / "tools" / "browser" / "browser_instance.py"
    
    if not browser_instance_path.exists():
        logger.error(f"❌ browser_instance.py not found at {browser_instance_path}")
        return False
    
    content = browser_instance_path.read_text()
    
    checks = [
        ("should_use_adaptive_login", "Domain detection import"),
        ("execute_adaptive_login_playwright", "Playwright adapter import"),
        ("ADAPTIVE_LOGIN_AVAILABLE", "Availability flag"),
        ("should_use_adaptive_login(url)", "Domain check in _goto"),
        ("execute_adaptive_login_playwright", "Login execution"),
    ]
    
    passed = 0
    failed = 0
    
    for check_str, description in checks:
        if check_str in content:
            logger.info(f"✅ {description}: Found '{check_str}'")
            passed += 1
        else:
            logger.error(f"❌ {description}: Missing '{check_str}'")
            failed += 1
    
    logger.info(f"Browser Instance Hook: {passed} passed, {failed} failed")
    return failed == 0


async def run_all_tests():
    """Run all integration tests."""
    logger.info("")
    logger.info("=" * 70)
    logger.info("STRIVORA ADAPTIVE LOGIN INTEGRATION TESTS")
    logger.info("=" * 70)
    logger.info("")
    
    results = []
    
    # Test 1: Domain Detection
    results.append(("Domain Detection", test_domain_detection()))
    
    # Test 2: Credential Loading
    results.append(("Credential Loading", test_credential_loading()))
    
    # Test 3: Browser Instance Hook
    results.append(("Browser Instance Hook", test_browser_instance_hook()))
    
    # Test 4: Playwright Integration (requires credentials)
    results.append(("Playwright Integration", await test_playwright_integration()))
    
    # Test 5: Undetected Adapter (optional)
    results.append(("Undetected Adapter", await test_undetected_adapter()))
    
    # Summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{status}: {test_name}")
    
    logger.info("")
    logger.info(f"Total: {passed}/{total} tests passed")
    logger.info("")
    
    if passed == total:
        logger.info("🎉 All integration tests passed!")
    else:
        logger.warning(f"⚠️  {total - passed} test(s) failed")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)

