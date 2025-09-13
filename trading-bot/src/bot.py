import logging
import time
from src.utils.file_helpers import load_state, save_state
from src.utils.math_helpers import money_to_points, trailing_steps
from src.strategies.trailing_sl import TrailingSL
from src.kite_client import KiteClient
from kiteconnect import KiteTicker
from src import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

state = load_state(config.STATE_FILE)
kite_client = KiteClient(config.API_KEY, config.ACCESS_TOKEN)

# -------------------------
# Load buy position
# -------------------------
def load_position():
    if state.get("buy_price") and state.get("position_qty"):
        return state["buy_price"], state["position_qty"]
    positions = kite_client.get_positions()
    for sec in ("day", "net"):
        for p in positions.get(sec, []):
            if p.get("tradingsymbol") == config.SYMBOL and float(p.get("quantity", 0)) > 0:
                state["buy_price"] = float(p.get("average_price"))
                state["position_qty"] = int(p.get("quantity"))
                save_state(state, config.STATE_FILE)
                logging.info("Loaded position buy_price=%.2f qty=%d", state["buy_price"], state["position_qty"])
                return state["buy_price"], state["position_qty"]
    logging.error("No BUY position found for %s", config.SYMBOL)
    return None, None

# -------------------------
# Run KiteTicker websocket
# -------------------------
def run_bot():
    buy_price, qty = load_position()
    if not buy_price:
        return

    sl_gap = money_to_points(config.RISK_RUPEES, config.QUANTITY, config.LOTS, config.RISK_MODE)
    target_gap = money_to_points(config.REWARD_RUPEES, config.QUANTITY, config.LOTS, config.RISK_MODE)
    trail_step = money_to_points(config.TRAIL_RUPEES, config.QUANTITY, config.LOTS, config.RISK_MODE)

    trailing_sl = TrailingSL(kite_client, config.SYMBOL, config.QUANTITY, config, state)

    # Place initial SL if not done
    if not state.get("sl_order_id"):
        initial_sl_trigger = buy_price - sl_gap
        trailing_sl.place_initial_sl(initial_sl_trigger)
        logging.info("Initial SL placed at %.2f", initial_sl_trigger)

    # -------------------------
    # KiteTicker callbacks
    # -------------------------
    kws = KiteTicker(config.API_KEY, config.ACCESS_TOKEN)
    instrument_token = None

    def on_connect(ws, response):
        nonlocal instrument_token
        try:
            ltp_resp = kite_client.kite.ltp(f"NFO:{config.SYMBOL}")
            key = f"NFO:{config.SYMBOL}"
            instrument_token = ltp_resp[key].get("instrument_token")
            logging.info("Websocket connected, subscribing to %s (token=%s)", config.SYMBOL, instrument_token)
            ws.subscribe([instrument_token])
            ws.set_mode(ws.MODE_FULL, [instrument_token])
        except Exception as e:
            logging.exception("Failed to subscribe websocket: %s", e)

    def on_ticks(ws, ticks):
        for t in ticks:
            if t.get("instrument_token") == instrument_token:
                ltp = t.get("last_price") or t.get("ltp") or t.get("last_traded_price")
                if ltp:
                    ltp = float(ltp)
                    handle_price(ltp)

    def on_close(ws, code, reason):
        logging.info("Websocket closed: code=%s reason=%s", code, reason)

    def handle_price(ltp):
        """
        Called on every LTP tick
        """
        # First target & initial SL
        first_target = buy_price + target_gap

        # If first target not hit yet
        if not state.get("first_target_hit", False) and ltp >= first_target:
            state["first_target_hit"] = True
            if config.FIRST_TARGET_SL_MODE == "BUY":
                new_sl = buy_price
            else:
                new_sl = (buy_price + first_target) / 2.0
            logging.info("First target hit (LTP=%.2f). Updating SL -> %.2f", ltp, new_sl)
            trailing_sl.modify_sl(new_sl)
            save_state(state, config.STATE_FILE)
            return

        # Trailing mode
        if state.get("first_target_hit", False) and ltp > first_target:
            if config.FIRST_TARGET_SL_MODE == "BUY":
                base_sl = buy_price
            else:
                base_sl = (buy_price + first_target) / 2.0
            new_sl = trailing_steps(base_sl, ltp, first_target, trail_step)
            current_sl = state.get("sl_trigger", 0.0)
            if new_sl > current_sl + config.MIN_SL_STEP:
                logging.info("Trailing SL update: LTP=%.2f new SL=%.4f current SL=%.4f", ltp, new_sl, current_sl)
                trailing_sl.modify_sl(new_sl)

    # -------------------------
    # Start websocket
    # -------------------------
    kws.on_connect = on_connect
    kws.on_ticks = on_ticks
    kws.on_close = on_close
    logging.info("Starting KiteTicker websocket (Ctrl+C to stop)...")
    kws.connect(threaded=False)
