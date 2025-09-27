import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# API CREDENTIALS
# ============================================================================
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_DATE = os.getenv("ACCESS_TOKEN_DATE")

# ============================================================================
# RISK MANAGEMENT SETTINGS
# ============================================================================
LOT_SIZE = int(os.getenv("LOT_SIZE", 75))  # Default to NIFTY lot size
RISK_RUPEES = float(os.getenv("RISK_RUPEES", 500))
REWARD_RUPEES = float(os.getenv("REWARD_RUPEES", 1000))
TRAIL_RUPEES = float(os.getenv("TRAIL_RUPEES", 100))

RISK_MODE = os.getenv("RISK_MODE", "PER_LOT").upper()  # PER_LOT or ABSOLUTE
FIRST_TARGET_SL_MODE = os.getenv("FIRST_TARGET_SL_MODE", "MIDPOINT").upper()  # BUY or MIDPOINT

# ============================================================================
# ORDER MANAGEMENT SETTINGS
# ============================================================================
ORDER_BUFFER = float(os.getenv("ORDER_BUFFER", 0.05))
MAX_MODIFY_BEFORE_RECREATE = int(os.getenv("MAX_MODIFY_BEFORE_RECREATE", 20))
THROTTLE_SECONDS = float(os.getenv("THROTTLE_SECONDS", 2.0))
MIN_SL_STEP = float(os.getenv("MIN_SL_STEP", 0.1))

# ============================================================================
# SYSTEM SETTINGS
# ============================================================================
STATE_FILE = os.getenv("STATE_FILE", "state.json")

# ============================================================================
# POSTBACK MODE - NO FILTERING NEEDED
# ============================================================================
# The bot handles ALL option contracts automatically:
# - Index options: NIFTY, BANKNIFTY, SENSEX, FINNIFTY, etc.
# - Stock options: RELIANCE, TCS, HDFCBANK, etc.  
# - Any other F&O contracts
# Postback provides exact symbol information, no filtering required
