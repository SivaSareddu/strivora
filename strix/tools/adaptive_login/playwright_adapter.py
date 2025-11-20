"""
Playwright Adapter for Adaptive Login

Adapts the adaptive login module to work with STRIVORA's Playwright browser instance.
"""
import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

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
    logger.warning("   Install ai_web_scraping project or copy adaptive_login.py to STRIVORA")
    ADAPTIVE_LOGIN_AVAILABLE = False


async def execute_adaptive_login_playwright(
    page: Any,
    email: str,
    password: str,
    login_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute adaptive login using Playwright Page object.
    
    Args:
        page: Playwright Page object
        email: Login email
        password: Login password
        login_url: Optional login URL (if different from current page)
        
    Returns:
        Dict with success status and details
    """
    if not ADAPTIVE_LOGIN_AVAILABLE:
        return {
            "success": False,
            "error": "Adaptive login module not available",
            "message": "Install ai_web_scraping project dependencies",
        }
    
    try:
        # Navigate to login URL if provided
        if login_url:
            logger.info(f"🌐 Navigating to login URL: {login_url}")
            await page.goto(login_url, wait_until="domcontentloaded")
            await asyncio.sleep(2)
        
        # Execute adaptive login
        logger.info("🔐 Starting adaptive login flow...")
        result = await execute_adaptive_multistep_login(
            driver=page,
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

