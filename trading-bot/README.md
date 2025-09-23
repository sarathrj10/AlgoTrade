# Trading Bot

An automated trading bot for Zerodha Kite API with trailing stop-loss functionality.

## Setup

1. Install dependencies using PDM:
   ```bash
   pdm install
   ```

2. **Configure your Zerodha API credentials** (choose one method):

   **Method A: Environment Variables (Recommended)**
   ```bash
   # Edit .env file and set your credentials:
   API_KEY=your_actual_api_key
   API_SECRET=your_actual_api_secret
   ```

   **Method B: Interactive Setup**
   ```bash
   pdm run auth    # Will prompt for credentials
   ```

## Authentication

The bot uses the `src/auth.py` module for Zerodha authentication with multiple credential sources:

1. **Environment variables** (`.env` file) - Checked first
2. **Saved credentials file** (`Login Credentials.json`) - Checked second  
3. **Interactive prompt** - Last resort

Features:
- Caches daily access tokens in `AccessToken/` directory
- Automatically handles token refresh
- No need to re-enter credentials once configured

### Usage

```python
from src.auth import ZerodhaAuth

auth = ZerodhaAuth()
credentials = auth.authenticate()
```

## Available Commands

### Authentication:
```bash
pdm run auth           # Set up Zerodha API credentials and authentication
```

### Running the Bot:
```bash
pdm run start          # Start the trading bot
```

### Development:
```bash
pdm run test           # Run tests
pdm run test-verbose   # Run tests with verbose output
pdm run test-coverage  # Run tests with coverage report
pdm run lint           # Run linting
```

## Quick Start

```bash
# First-time setup
pdm install
pdm run auth
pdm run start

# Daily usage
pdm run start
```