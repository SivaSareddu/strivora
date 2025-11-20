# Adaptive Login Integration for STRIVORA

## Overview

This integration adds automatic adaptive login support for T-Mobile domains (`my.t-mobile.com`, `account.t-mobile.com`, `www.t-mobile.com`) when using STRIVORA for security testing.

## Features

- ✅ **Automatic Domain Detection**: Detects T-Mobile domains and triggers adaptive login
- ✅ **Playwright Integration**: Works with STRIVORA's existing Playwright browser
- ✅ **Undetected Chrome Support**: Optional undetected-chromedriver for better bot evasion
- ✅ **AI Vision Powered**: Uses AI Vision to handle complex multi-step login flows
- ✅ **MFA Support**: Handles MFA prompts and waits for human input when needed

## Installation

### 1. Install Dependencies

```bash
cd /Users/ssaredd/workspace/strivora
poetry add undetected-chromedriver python-dotenv selenium
# OR
pip install undetected-chromedriver python-dotenv selenium
```

### 2. Set Environment Variables

Create a `.env` file or export:

```bash
export TMO_LOGIN="your-email@example.com"
export TMO_PASSWORD="your-password"
export OPENAI_API_KEY="your-openai-api-key"  # Required for AI Vision
```

### 3. Ensure ai_web_scraping Project is Available

The adaptive login module references the `ai_web_scraping` project. Make sure it's accessible at:
- `/Users/ssaredd/workspace/ai_web_scraping`

The adapters will automatically add it to the Python path.

## Architecture

### Files Created

```
strix/tools/adaptive_login/
├── __init__.py                 # Module exports
├── domain_detector.py          # Detects T-Mobile domains
├── playwright_adapter.py      # Playwright integration
└── undetected_adapter.py       # Undetected Chrome integration
```

### Integration Points

1. **`browser_instance.py`**: Modified `_goto()` method to check for adaptive login domains
2. **Domain Detection**: Automatically detects T-Mobile domains in URLs
3. **Credential Loading**: Loads credentials from environment variables

## How It Works

1. **User runs STRIVORA**:
   ```bash
   strix --target https://my.t-mobile.com
   ```

2. **Domain Detection**: When `browser_instance.goto()` is called, it checks if the URL matches a T-Mobile domain

3. **Credential Loading**: If detected, loads `TMO_LOGIN` and `TMO_PASSWORD` from environment

4. **Adaptive Login Execution**: 
   - Navigates to login URL
   - Uses AI Vision to analyze page state
   - Handles popups (privacy, cookies)
   - Fills email and clicks Next
   - Handles password entry
   - Manages MFA flow (waits for human input if needed)

5. **Continues Testing**: After successful login, STRIVORA continues with security testing

## Testing

### Simple Domain Detection Test

```bash
cd /Users/ssaredd/workspace/strivora
python test_adaptive_login_simple.py
```

### Full Integration Test

```bash
# Set credentials first
export TMO_LOGIN="your-email@example.com"
export TMO_PASSWORD="your-password"
export OPENAI_API_KEY="your-key"

# Run test
python test_adaptive_login_integration.py
```

### Test with STRIVORA CLI

```bash
# Set credentials
export TMO_LOGIN="your-email@example.com"
export TMO_PASSWORD="your-password"
export OPENAI_API_KEY="your-key"

# Run STRIVORA - adaptive login will trigger automatically
strix --target https://my.t-mobile.com
```

## Configuration

### Adding New Domains

Edit `strix/tools/adaptive_login/domain_detector.py`:

```python
ADAPTIVE_LOGIN_DOMAINS = {
    "my.t-mobile.com": {
        "enabled": True,
        "email_env": "TMO_LOGIN",
        "password_env": "TMO_PASSWORD",
        "login_url": "https://account.t-mobile.com/signin/v2/",
        "description": "T-Mobile multi-step login with MFA support",
    },
    # Add your domain here
    "your-domain.com": {
        "enabled": True,
        "email_env": "YOUR_LOGIN",
        "password_env": "YOUR_PASSWORD",
        "login_url": "https://your-domain.com/login",
        "description": "Your domain login",
    },
}
```

## Implementation Details

### Playwright Adapter

- Uses STRIVORA's existing Playwright browser instance
- No additional browser launch required
- Seamlessly integrates with existing browser actions

### Undetected Chrome Adapter

- Creates separate Chrome instance using `undetected-chromedriver`
- Better bot detection evasion
- Persistent browser profiles for session management
- Can be used independently or as fallback

### AI Vision Integration

The adaptive login uses OpenAI's GPT-4 Vision API to:
- Analyze page screenshots
- Detect page types (login, password, MFA, error, etc.)
- Find form fields and buttons
- Handle dynamic UI changes
- Adapt to different login flows

## Troubleshooting

### "Adaptive login module not available"

- Ensure `ai_web_scraping` project exists at `/Users/ssaredd/workspace/ai_web_scraping`
- Check that `worker/agents/adaptive_login.py` exists in that project

### "Credentials not found"

- Set `TMO_LOGIN` and `TMO_PASSWORD` environment variables
- Or create `.env` file in STRIVORA directory

### "OpenAI API key not set"

- Set `OPENAI_API_KEY` environment variable
- Required for AI Vision analysis

### Import Errors

If you see import errors related to `tree_sitter_languages` or other STRIVORA dependencies:
- Install STRIVORA dependencies: `poetry install` or `pip install -r requirements.txt`
- Or test domain detection directly without importing full STRIVORA modules

## Status

✅ **Completed**:
- Domain detection module
- Playwright adapter
- Undetected Chrome adapter
- Browser integration hook
- Test scripts

🔄 **In Progress**:
- Full end-to-end testing

📝 **Future Enhancements**:
- Support for more domains
- Configurable login strategies
- Session persistence
- Multi-account support

