# STRIVORA Adaptive Login Integration Test Guide

## Quick Start

### 1. Set Environment Variables

```bash
export TMO_LOGIN="your-email@example.com"
export TMO_PASSWORD="your-password"
export OPENAI_API_KEY="your-openai-api-key"
export STRIX_LLM="openai/gpt-4o"
export LLM_API_KEY="your-openai-api-key"
```

Or create a `.env` file:

```bash
TMO_LOGIN=your-email@example.com
TMO_PASSWORD=your-password
OPENAI_API_KEY=your-openai-api-key
STRIX_LLM=openai/gpt-4o
LLM_API_KEY=your-openai-api-key
```

### 2. Run Integration Tests

```bash
cd /Users/ssaredd/workspace/strivora

# Run all integration tests
python tests/test_adaptive_login_integration.py

# Or run CLI test
python tests/test_strix_cli_with_adaptive_login.py
```

### 3. Test with STRIVORA CLI

```bash
# Test with T-Mobile domain (adaptive login will trigger automatically)
strix --target https://my.t-mobile.com

# Or with account domain
strix --target https://account.t-mobile.com/signin/v2/
```

## Test Methods

### Method 1: Unit Tests (Fastest)

Test individual components without full browser:

```bash
# Test domain detection
python -c "
from strix.tools.adaptive_login.domain_detector import should_use_adaptive_login, get_login_config
print('my.t-mobile.com:', should_use_adaptive_login('https://my.t-mobile.com'))
print('example.com:', should_use_adaptive_login('https://example.com'))
config = get_login_config('https://my.t-mobile.com')
print('Config:', config is not None)
"
```

### Method 2: Integration Tests

Run comprehensive integration tests:

```bash
python tests/test_adaptive_login_integration.py
```

This tests:
- ✅ Domain detection logic
- ✅ Credential loading
- ✅ Browser instance hook
- ✅ Playwright integration
- ✅ Undetected adapter availability

### Method 3: Full STRIVORA CLI Test

Test the complete flow with actual STRIVORA:

```bash
# Set credentials
export TMO_LOGIN="your-email@example.com"
export TMO_PASSWORD="your-password"
export OPENAI_API_KEY="your-key"
export STRIX_LLM="openai/gpt-4o"
export LLM_API_KEY="your-key"

# Run STRIVORA
strix --target https://my.t-mobile.com
```

**Expected Output:**
```
🔐 Adaptive login detected for domain: https://my.t-mobile.com
🚀 Executing adaptive login for my.t-mobile.com...
📸 Analyzing current page state with Vision...
✅ Adaptive login successful: login_completed
```

### Method 4: Python Script Test

Test with a custom Python script:

```python
import asyncio
import os
from strix.tools.browser.browser_instance import BrowserInstance

async def test():
    browser = BrowserInstance()
    browser.launch()
    
    # Navigate to T-Mobile - adaptive login will trigger
    result = browser.goto("https://my.t-mobile.com")
    print(result)
    
    browser.close()

asyncio.run(test())
```

## What Gets Tested

### 1. Domain Detection ✅
- Detects `my.t-mobile.com`
- Detects `account.t-mobile.com`
- Detects `www.t-mobile.com`
- Ignores non-T-Mobile domains

### 2. Credential Loading ✅
- Loads `TMO_LOGIN` from environment
- Loads `TMO_PASSWORD` from environment
- Returns `None` if credentials missing

### 3. Browser Integration ✅
- `browser_instance._goto()` checks for adaptive login
- Triggers login automatically when domain matches
- Continues normal flow after login

### 4. Adaptive Login Flow ✅
- Handles popups (privacy, cookies)
- Fills email and clicks Next
- Handles password entry
- Manages MFA flow
- Uses AI Vision for page analysis

## Troubleshooting

### "Adaptive login module not available"

**Solution:**
```bash
# Ensure ai_web_scraping project exists
ls /Users/ssaredd/workspace/ai_web_scraping/worker/agents/adaptive_login.py

# If missing, the adapters will show a warning but won't fail
```

### "Credentials not found"

**Solution:**
```bash
# Set environment variables
export TMO_LOGIN="your-email@example.com"
export TMO_PASSWORD="your-password"

# Verify
echo $TMO_LOGIN
echo $TMO_PASSWORD
```

### "OpenAI API key not set"

**Solution:**
```bash
export OPENAI_API_KEY="your-openai-api-key"

# Verify
echo $OPENAI_API_KEY
```

### "undetected-chromedriver not available"

**Solution:**
```bash
pip install undetected-chromedriver
# OR
poetry add undetected-chromedriver
```

### Import Errors

If you see import errors related to STRIVORA dependencies:

```bash
# Install STRIVORA dependencies
cd /Users/ssaredd/workspace/strivora
poetry install
# OR
pip install -r requirements.txt
```

## Test Output Examples

### Successful Test

```
======================================================================
STRIVORA ADAPTIVE LOGIN INTEGRATION TESTS
======================================================================

======================================================================
TEST 1: Domain Detection
======================================================================
✅ https://my.t-mobile.com/dashboard
   Domain: my.t-mobile.com (expected: my.t-mobile.com)
   Detected: True (expected: True)

✅ https://example.com/login
   Domain: example.com (expected: example.com)
   Detected: False (expected: False)

Domain Detection: 6 passed, 0 failed

======================================================================
TEST SUMMARY
======================================================================
✅ PASSED: Domain Detection
✅ PASSED: Credential Loading
✅ PASSED: Browser Instance Hook
✅ PASSED: Playwright Integration
✅ PASSED: Undetected Adapter

Total: 5/5 tests passed

🎉 All integration tests passed!
```

### Failed Test (Missing Credentials)

```
⚠️  TMO_LOGIN and TMO_PASSWORD not set
   Set environment variables to test Playwright integration
   Skipping this test...

⚠️  Missing required environment variables:
   export TMO_LOGIN='your-value'
   export TMO_PASSWORD='your-value'
```

## Continuous Integration

To run tests in CI/CD:

```yaml
# Example GitHub Actions
- name: Run Integration Tests
  env:
    TMO_LOGIN: ${{ secrets.TMO_LOGIN }}
    TMO_PASSWORD: ${{ secrets.TMO_PASSWORD }}
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: |
    python tests/test_adaptive_login_integration.py
```

## Next Steps

After running tests:

1. **Verify Domain Detection**: Ensure T-Mobile domains are detected
2. **Test Credentials**: Verify credentials load correctly
3. **Test Browser Integration**: Run STRIVORA with T-Mobile domain
4. **Monitor Logs**: Watch for adaptive login triggers
5. **Verify Login Success**: Check that login completes successfully

## Support

For issues:
1. Check environment variables are set
2. Verify `ai_web_scraping` project is accessible
3. Check STRIVORA dependencies are installed
4. Review logs for specific error messages

