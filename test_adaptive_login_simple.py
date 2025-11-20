#!/usr/bin/env python3
"""
Simple test script for adaptive login integration.
Tests domain detection without requiring full STRIVORA setup.
"""
import os
import sys
from pathlib import Path

# Add STRIVORA to path
strivora_path = Path(__file__).parent
sys.path.insert(0, str(strivora_path))

# Test domain detection
try:
    from strix.tools.adaptive_login.domain_detector import (
        should_use_adaptive_login,
        get_login_config,
        extract_domain,
    )
    
    print("=" * 60)
    print("ADAPTIVE LOGIN DOMAIN DETECTION TEST")
    print("=" * 60)
    print()
    
    test_urls = [
        "https://my.t-mobile.com/dashboard",
        "https://account.t-mobile.com/signin/v2/",
        "https://www.t-mobile.com/account",
        "https://example.com/login",
    ]
    
    for url in test_urls:
        domain = extract_domain(url)
        should_use = should_use_adaptive_login(url)
        config = get_login_config(url)
        
        print(f"URL: {url}")
        print(f"  Domain: {domain}")
        print(f"  Should use adaptive login: {should_use}")
        if config:
            print(f"  ✅ Config found!")
            print(f"     Email env: {config.get('email', 'NOT SET')[:20]}...")
            print(f"     Login URL: {config.get('login_url')}")
        else:
            print(f"  ⚠️  Config: None (credentials may not be set)")
        print()
    
    print("=" * 60)
    print("INTEGRATION STATUS")
    print("=" * 60)
    print()
    print("✅ Domain detector module: WORKING")
    
    # Check if adapters are available
    try:
        from strix.tools.adaptive_login.playwright_adapter import execute_adaptive_login_playwright
        print("✅ Playwright adapter: AVAILABLE")
    except ImportError as e:
        print(f"⚠️  Playwright adapter: {e}")
    
    try:
        from strix.tools.adaptive_login.undetected_adapter import execute_adaptive_login_undetected
        print("✅ Undetected adapter: AVAILABLE")
    except ImportError as e:
        print(f"⚠️  Undetected adapter: {e}")
    
    print()
    print("=" * 60)
    print("HOW TO USE")
    print("=" * 60)
    print()
    print("1. Set environment variables:")
    print("   export TMO_LOGIN='your-email@example.com'")
    print("   export TMO_PASSWORD='your-password'")
    print()
    print("2. When STRIVORA navigates to my.t-mobile.com or account.t-mobile.com,")
    print("   adaptive login will automatically trigger.")
    print()
    print("3. The browser_instance.py _goto() method has been modified to:")
    print("   - Detect T-Mobile domains")
    print("   - Load credentials from environment")
    print("   - Execute adaptive login flow")
    print()
    print("4. Test with STRIVORA:")
    print("   strix --target https://my.t-mobile.com")
    print()
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print()
    print("Make sure you're running from the STRIVORA directory")
    sys.exit(1)

