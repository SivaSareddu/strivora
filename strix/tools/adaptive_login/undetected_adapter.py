"""
Undetected Chrome Adapter for Adaptive Login

Uses undetected-chromedriver for better bot detection evasion.
"""
import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Try to import undetected_chromedriver
try:
    import undetected_chromedriver as uc
    UNDETECTED_CHROME_AVAILABLE = True
except ImportError:
    logger.warning("⚠️  undetected-chromedriver not available. Install with: pip install undetected-chromedriver")
    UNDETECTED_CHROME_AVAILABLE = False

# Try to import adaptive_login from ai_web_scraping project
try:
    # Add ai_web_scraping to path if available
    ai_web_scraping_path = Path(__file__).parent.parent.parent.parent.parent / "ai_web_scraping"
    if ai_web_scraping_path.exists():
        sys.path.insert(0, str(ai_web_scraping_path))
        sys.path.insert(0, str(ai_web_scraping_path / "worker"))
        sys.path.insert(0, str(ai_web_scraping_path / "common"))
    
    from worker.agents.adaptive_login import (
        execute_adaptive_multistep_login,
        analyze_current_page_state,
        detect_and_handle_popups,
    )
    ADAPTIVE_LOGIN_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️  Adaptive login module not available: {e}")
    ADAPTIVE_LOGIN_AVAILABLE = False


def create_undetected_chrome_driver(
    headless: bool = False,
    profile_name: str = "strivora_profile",
) -> Optional[Any]:
    """
    Create undetected-chromedriver instance with persistent profile.
    
    Args:
        headless: Whether to run in headless mode
        profile_name: Name of the profile directory
        
    Returns:
        WebDriver instance or None if unavailable
    """
    if not UNDETECTED_CHROME_AVAILABLE:
        logger.error("❌ undetected-chromedriver not available")
        return None
    
    try:
        # Create persistent profile directory
        base_path = Path(__file__).parent.parent.parent.parent.parent
        profile_dir = base_path / "browser_profiles" / profile_name
        profile_dir.mkdir(parents=True, exist_ok=True)
        
        user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/142.0.0.0 Safari/537.36"
        )
        
        options = uc.ChromeOptions()
        
        # Use persistent user data directory
        options.add_argument(f"--user-data-dir={profile_dir}")
        options.add_argument(f"user-agent={user_agent}")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--lang=en-US")
        options.add_experimental_option(
            "prefs",
            {
                "intl.accept_languages": "en-US,en",
                "profile.default_content_setting_values.notifications": 2,
            },
        )
        
        if headless:
            options.add_argument("--headless=new")
        
        driver = uc.Chrome(options=options, version_main=None)
        logger.info(f"✅ Undetected Chrome driver created (profile: {profile_name})")
        return driver
        
    except Exception as e:
        logger.error(f"❌ Failed to create undetected Chrome driver: {e}")
        return None


async def execute_adaptive_login_undetected(
    email: str,
    password: str,
    login_url: str,
    headless: bool = False,
    profile_name: str = "strivora_profile",
) -> Dict[str, Any]:
    """
    Execute adaptive login using undetected-chromedriver.
    
    Args:
        email: Login email
        password: Login password
        login_url: Login URL to navigate to
        headless: Whether to run in headless mode
        profile_name: Profile name for persistence
        
    Returns:
        Dict with success status and details
    """
    if not ADAPTIVE_LOGIN_AVAILABLE:
        return {
            "success": False,
            "error": "Adaptive login module not available",
        }
    
    if not UNDETECTED_CHROME_AVAILABLE:
        return {
            "success": False,
            "error": "undetected-chromedriver not available",
        }
    
    driver = None
    try:
        # Create driver
        driver = create_undetected_chrome_driver(headless=headless, profile_name=profile_name)
        if not driver:
            return {
                "success": False,
                "error": "Failed to create Chrome driver",
            }
        
        # Navigate to login URL
        logger.info(f"🌐 Navigating to login URL: {login_url}")
        driver.get(login_url)
        await asyncio.sleep(2)
        
        # Execute adaptive login
        logger.info("🔐 Starting adaptive login flow with undetected Chrome...")
        result = await execute_adaptive_multistep_login(
            driver=driver,
            email=email,
            password=password,
        )
        
        if result.get("success"):
            logger.info(f"✅ Adaptive login completed: {result.get('stage')}")
        else:
            logger.warning(f"⚠️  Adaptive login failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Adaptive login exception: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "stage": "exception",
        }
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

