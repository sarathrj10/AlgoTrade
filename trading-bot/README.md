# Trading Bot

An automated trading bot for Zerodha Kite API with trailing stop-loss functionality.

# Dynamic Trading Bot

This bot automatically detects when you place BUY orders manually in Kite and starts trailing stop-loss (SL) management for those positions using **real-time postback notifications**.

## How It Works

### Step 1: Place Orders Manually
- Place your BUY orders manually in Kite (web/mobile app)
- The bot doesn't need to know which symbols you're trading beforehand

### Step 2: Instant Detection via Postback
- Zerodha sends instant HTTP POST request to your postback URL when order executes
- Bot receives real-time notification (0 delay)
- No API polling needed - completely event-driven

### Step 3: Automatic Trailing SL
- Bot immediately places an initial stop-loss based on your risk settings
- Subscribes to real-time market data for that symbol
- Starts trailing SL logic automatically

## Features

✅ **Real-time Detection** - Instant postback notifications (0ms delay)  
✅ **Universal Coverage** - Works with ALL option contracts (index + stock options)  
✅ **Multiple Positions** - Handles multiple positions simultaneously  
✅ **Auto Recovery** - Restores positions on bot restart  
✅ **Efficient** - No unnecessary polling or API calls  
✅ **Robust Error Handling** - Continues running even if some operations fail  
✅ **Optional Ngrok Integration** - Automatic tunnel creation for quick testing

## Quick Start

### Prerequisites
```bash
# Install dependencies (includes optional pyngrok)
pdm install

# If pyngrok is missing, install separately:
pip install pyngrok
```  

## Usage

### Single Command - Integrated Postback Server

```bash
cd trading-bot
pdm run python scripts/run_bot.py
```

**What this does:**
1. 🚀 Starts the Dynamic Trading Bot
2. 🌐 Starts Flask postback server on port 5000
3. 📡 Receives real-time order notifications from Zerodha
4. 🎯 Automatically manages trailing SL for detected positions

**Setup Steps:**
1. Run the command above
2. For **local testing**: Use ngrok to expose port: `ngrok http 5001`
3. For **production**: Deploy on cloud server with proper domain
4. **Configure postback URL** in Zerodha app: 
   - Local: `https://your-ngrok-url.ngrok.io/postback`
   - Production: `https://yourdomain.com/postback`
5. **Place orders in Kite** - bot gets INSTANT notifications!

**Why this is the only method you need:**
- ⚡ **Real-time** - 0ms delay order detection
- 🚫 **No API limits** - Zerodha pushes data to you
- 💰 **Efficient** - No polling, no wasted resources
- 🎯 **Reliable** - Never misses an order
- 🔧 **Simple** - Single command, everything integrated

## Postback Setup

### Automatic ngrok Setup (Recommended for Quick Testing):
```bash
# Enable automatic ngrok tunnel in your .env file
USE_NGROK=true

# Optional: Add your ngrok auth token for better stability
NGROK_AUTH_TOKEN=your_auth_token_here

# Start the bot - ngrok tunnel is created automatically!
pdm run python scripts/run_bot.py
```

**What happens:**
- ✅ Bot automatically creates ngrok tunnel 
- ✅ Shows you the public URL to use in Zerodha settings
- ✅ No need to run ngrok separately
- ✅ Tunnel is cleaned up when bot stops

### Manual ngrok Setup:
```bash
# Terminal 1: Start the bot
pdm run python scripts/run_bot.py

# Terminal 2: Expose to internet
ngrok http 5001

# Use the ngrok URL in Zerodha settings:
# https://abc123.ngrok.io/postback
```

### Production Setup:
1. Deploy on cloud server (AWS, Digital Ocean, etc.)
2. Set up proper domain/SSL
3. Configure: `https://yourdomain.com/postback`
4. Ensure server is always running

## Configuration

Update your `.env` file with these settings:

```env
# API Credentials
API_KEY=your_api_key
API_SECRET=your_api_secret

# Risk Management (Per Position)
RISK_RUPEES=500          # Risk per position in rupees
REWARD_RUPEES=1000       # Target profit per position in rupees  
TRAIL_RUPEES=100         # Trailing step in rupees

# Risk Mode
RISK_MODE=PER_LOT        # PER_LOT or ABSOLUTE
FIRST_TARGET_SL_MODE=MIDPOINT  # BUY (breakeven) or MIDPOINT

# Ngrok Settings (Optional - for quick testing)
USE_NGROK=true           # Automatically create ngrok tunnel
NGROK_AUTH_TOKEN=your_token_here  # Optional: for better stability

# Order Settings  
ORDER_BUFFER=0.05        # Buffer for SL orders
THROTTLE_SECONDS=2.0     # Throttle between order modifications
MIN_SL_STEP=0.1          # Minimum SL movement step
```

## How Trailing SL Works

1. **Initial SL**: Placed immediately when BUY order is detected
   - SL Trigger = Buy Price - Risk Amount (in points)

2. **First Target**: When price reaches reward target
   - If `FIRST_TARGET_SL_MODE=BUY`: Move SL to breakeven (buy price)
   - If `FIRST_TARGET_SL_MODE=MIDPOINT`: Move SL to midpoint between buy price and target

3. **Trailing**: After first target, SL trails price upward
   - Trails in steps defined by `TRAIL_RUPEES`
   - Never moves down, only up

## Supported Instruments

The bot automatically handles **ALL option contracts**:

### Index Options:
- NIFTY, BANKNIFTY, SENSEX, FINNIFTY, MIDCPNIFTY

### Stock Options:
- RELIANCE, TCS, HDFCBANK, INFY, WIPRO, etc.

### Any F&O Contracts:
- Whatever symbol comes in the postback notification

## State Management

- Bot saves position state in `state.json`
- Automatically restores positions on restart
- Handles bot crashes gracefully

## Example Workflow

1. **Start Bot**: `pdm run python scripts/run_bot.py`
2. **Place Order**: Buy any option manually in Kite (e.g., RELIANCE24000CE or NIFTY25000PE)
3. **Auto Detection**: Bot detects execution via postback
4. **Auto SL**: Bot places initial SL based on your risk settings
5. **Auto Trailing**: Bot monitors and trails SL as price moves favorably

## Monitoring

Watch the console output for:
- New position detection
- SL placements and modifications  
- Trailing updates
- Error messages

## Troubleshooting

### Common Issues:

1. **"No postback notifications received"**
   - Check if postback URL is correctly configured in Zerodha app
   - Ensure your server/ngrok is accessible from internet
   - Verify Flask server is running on port 5000

2. **"Failed to get instrument token"**
   - Check if symbol format is correct
   - Ensure market is open for that instrument

3. **"Failed to place initial SL"**  
   - Check if you have sufficient margin
   - Verify order placement permissions

### Getting Help:

- Check logs for detailed error messages
- Ensure all dependencies are installed: `pdm install`
- Verify `.env` configuration

## Safety Features

- Only processes BUY orders (ignores sells)
- Handles ALL option contracts automatically
- Maintains separate state for each position
- Graceful error handling - continues running if one position fails
- Never moves SL in unfavorable direction

## Advantages over Manual SL

✅ **Instant Response** - Places SL immediately after execution  
✅ **Never Misses** - Doesn't require you to watch the screen  
✅ **Precise Trailing** - Follows exact mathematical rules  
✅ **Multiple Positions** - Handles many trades simultaneously  
✅ **Universal Coverage** - Works with any option contract  
✅ **No Emotions** - Sticks to predefined rules  
✅ **24/7 Monitoring** - Works even when you're not watching

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