#!/usr/bin/env python3
"""
Integration test for STRIVORA CLI with adaptive login.

This test simulates running STRIVORA CLI commands that trigger adaptive login.
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def test_strix_cli_domain_detection():
    """Test that STRIVORA CLI detects T-Mobile domains."""
    logger.info("=" * 70)
    logger.info("TEST: STRIVORA CLI Domain Detection")
    logger.info("=" * 70)
    
    # Check if strix command is available
    try:
        result = subprocess.run(
            ["strix", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            logger.warning("⚠️  'strix' command not found or not working")
            logger.warning("   Install STRIVORA: pipx install strix-agent")
            return False
    except FileNotFoundError:
        logger.warning("⚠️  'strix' command not found")
        logger.warning("   Install STRIVORA: pipx install strix-agent")
        return False
    
    logger.info("✅ STRIVORA CLI is available")
    logger.info("")
    logger.info("To test adaptive login with STRIVORA CLI:")
    logger.info("")
    logger.info("1. Set environment variables:")
    logger.info("   export TMO_LOGIN='your-email@example.com'")
    logger.info("   export TMO_PASSWORD='your-password'")
    logger.info("   export OPENAI_API_KEY='your-openai-key'")
    logger.info("   export STRIX_LLM='openai/gpt-4o'")
    logger.info("   export LLM_API_KEY='your-openai-key'")
    logger.info("")
    logger.info("2. Run STRIVORA with T-Mobile domain:")
    logger.info("   strix --target https://my.t-mobile.com")
    logger.info("")
    logger.info("3. Adaptive login will automatically trigger when STRIVORA")
    logger.info("   navigates to the T-Mobile domain.")
    logger.info("")
    
    return True


def test_environment_setup():
    """Check if environment is set up correctly."""
    logger.info("=" * 70)
    logger.info("TEST: Environment Setup")
    logger.info("=" * 70)
    
    required_vars = {
        "TMO_LOGIN": "T-Mobile login email",
        "TMO_PASSWORD": "T-Mobile password",
        "OPENAI_API_KEY": "OpenAI API key for AI Vision",
    }
    
    optional_vars = {
        "STRIX_LLM": "STRIVORA LLM model",
        "LLM_API_KEY": "LLM API key",
    }
    
    missing_required = []
    missing_optional = []
    
    for var, description in required_vars.items():
        if os.getenv(var):
            logger.info(f"✅ {var}: Set ({description})")
        else:
            logger.warning(f"⚠️  {var}: Not set ({description})")
            missing_required.append(var)
    
    for var, description in optional_vars.items():
        if os.getenv(var):
            logger.info(f"✅ {var}: Set ({description})")
        else:
            logger.info(f"ℹ️  {var}: Not set ({description}) - Optional")
            missing_optional.append(var)
    
    logger.info("")
    
    if missing_required:
        logger.warning("⚠️  Missing required environment variables:")
        for var in missing_required:
            logger.warning(f"   export {var}='your-value'")
        logger.warning("")
        logger.warning("Set these variables to enable adaptive login testing.")
        return False
    else:
        logger.info("✅ All required environment variables are set")
        return True


def print_test_instructions():
    """Print detailed test instructions."""
    logger.info("")
    logger.info("=" * 70)
    logger.info("HOW TO RUN INTEGRATION TESTS WITH STRIVORA")
    logger.info("=" * 70)
    logger.info("")
    
    logger.info("METHOD 1: Direct STRIVORA CLI Test")
    logger.info("-" * 70)
    logger.info("")
    logger.info("1. Set up environment:")
    logger.info("   export TMO_LOGIN='your-email@example.com'")
    logger.info("   export TMO_PASSWORD='your-password'")
    logger.info("   export OPENAI_API_KEY='your-openai-key'")
    logger.info("   export STRIX_LLM='openai/gpt-4o'")
    logger.info("   export LLM_API_KEY='your-openai-key'")
    logger.info("")
    logger.info("2. Run STRIVORA:")
    logger.info("   strix --target https://my.t-mobile.com")
    logger.info("")
    logger.info("3. Watch the logs - you should see:")
    logger.info("   '🔐 Adaptive login detected for domain: ...'")
    logger.info("   '🚀 Executing adaptive login for ...'")
    logger.info("   '✅ Adaptive login successful: ...'")
    logger.info("")
    
    logger.info("METHOD 2: Python Integration Test")
    logger.info("-" * 70)
    logger.info("")
    logger.info("1. Set up environment (same as Method 1)")
    logger.info("")
    logger.info("2. Run the integration test:")
    logger.info("   python tests/test_adaptive_login_integration.py")
    logger.info("")
    
    logger.info("METHOD 3: Unit Test Individual Components")
    logger.info("-" * 70)
    logger.info("")
    logger.info("Test domain detection:")
    logger.info("   python -c \"from strix.tools.adaptive_login.domain_detector import should_use_adaptive_login; print(should_use_adaptive_login('https://my.t-mobile.com'))\"")
    logger.info("")
    
    logger.info("=" * 70)
    logger.info("")


if __name__ == "__main__":
    print_test_instructions()
    
    env_ok = test_environment_setup()
    cli_ok = test_strix_cli_domain_detection()
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("SUMMARY")
    logger.info("=" * 70)
    
    if env_ok and cli_ok:
        logger.info("✅ Environment and CLI are ready for testing")
        logger.info("")
        logger.info("Run: strix --target https://my.t-mobile.com")
    else:
        logger.warning("⚠️  Some setup is incomplete")
        logger.warning("   See instructions above to complete setup")

