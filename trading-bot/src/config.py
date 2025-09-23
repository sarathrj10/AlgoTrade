import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

SYMBOL = os.getenv("SYMBOL")
LOTS = int(os.getenv("LOTS", 1))
LOT_SIZE = int(os.getenv("LOT_SIZE", 75))
QUANTITY = LOTS * LOT_SIZE
PRODUCT = os.getenv("PRODUCT", "NRML")

RISK_RUPEES = float(os.getenv("RISK_RUPEES", 500))
REWARD_RUPEES = float(os.getenv("REWARD_RUPEES", 1000))
TRAIL_RUPEES = float(os.getenv("TRAIL_RUPEES", 100))

RISK_MODE = os.getenv("RISK_MODE", "PER_LOT").upper()
FIRST_TARGET_SL_MODE = os.getenv("FIRST_TARGET_SL_MODE", "MIDPOINT").upper()

ORDER_BUFFER = float(os.getenv("ORDER_BUFFER", 0.05))
MAX_MODIFY_BEFORE_RECREATE = int(os.getenv("MAX_MODIFY_BEFORE_RECREATE", 20))
THROTTLE_SECONDS = float(os.getenv("THROTTLE_SECONDS", 2.0))
MIN_SL_STEP = float(os.getenv("MIN_SL_STEP", 0.1))
STATE_FILE = os.getenv("STATE_FILE", "state.json")
