import logging
import time
from typing import Dict, Optional, Set
from src.utils.file_helpers import load_state, save_state
from src.utils.math_helpers import money_to_points, trailing_steps
from src.strategies.trailing_sl import TrailingSL
from src.kite_client import KiteClient
from kiteconnect import KiteTicker
from src import config

"""
DYNAMIC BOT - Auto-detects positions and starts trailing SL
=========================================================
This bot automatically detects when you place BUY orders manually in Kite
and starts trailing stop-loss management for those positions.

Usage: python scripts/run_bot.py
"""

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

class DynamicTradingBot:
    def __init__(self):
        self.kite_client = KiteClient()
        self.active_positions: Dict[str, dict] = {}  # symbol -> position info
        self.market_ws = None
        self.subscribed_tokens: Set[int] = set()
        self.state = load_state(config.STATE_FILE)
        
    def get_instrument_token(self, symbol: str) -> Optional[int]:
        """Get instrument token for a symbol"""
        try:
            ltp_resp = self.kite_client.kite.ltp(f"NFO:{symbol}")
            key = f"NFO:{symbol}"
            return ltp_resp[key].get("instrument_token")
        except Exception as e:
            logging.error(f"Failed to get instrument token for {symbol}: {e}")
            return None

    def start_trailing_for_position(self, symbol: str, buy_price: float, quantity: int):
        """Start trailing SL logic for a position"""
        logging.info(f"Starting trailing SL for {symbol}: price={buy_price}, qty={quantity}")
        
        # Calculate gaps based on quantity (assuming standard lot sizes)
        lots = max(1, quantity // 75)  # Assuming standard lot size of 75
        sl_gap = money_to_points(config.RISK_RUPEES, quantity, lots, config.RISK_MODE)
        target_gap = money_to_points(config.REWARD_RUPEES, quantity, lots, config.RISK_MODE)
        trail_step = money_to_points(config.TRAIL_RUPEES, quantity, lots, config.RISK_MODE)
        
        # Create position-specific state
        position_state = {
            'buy_price': buy_price,
            'position_qty': quantity,
            'first_target_hit': False,
            'sl_order_id': None,
            'sl_trigger': 0.0
        }
        
        # Create position info
        position_info = {
            'symbol': symbol,
            'buy_price': buy_price,
            'quantity': quantity,
            'sl_gap': sl_gap,
            'target_gap': target_gap,
            'trail_step': trail_step,
            'first_target_hit': False,
            'sl_order_id': None,
            'sl_trigger': 0.0,
            'trailing_sl': TrailingSL(self.kite_client, symbol, quantity, config, position_state)
        }
        
        # Place initial SL
        initial_sl_trigger = buy_price - sl_gap
        try:
            sl_order_id = position_info['trailing_sl'].place_initial_sl(initial_sl_trigger)
            position_info['sl_order_id'] = sl_order_id
            position_info['sl_trigger'] = initial_sl_trigger
            logging.info(f"Initial SL placed for {symbol} at {initial_sl_trigger}")
        except Exception as e:
            logging.error(f"Failed to place initial SL for {symbol}: {e}")
            return
        
        # Store position
        self.active_positions[symbol] = position_info
        
        # Save to global state for persistence
        if 'active_positions' not in self.state:
            self.state['active_positions'] = {}
        self.state['active_positions'][symbol] = {
            'buy_price': buy_price,
            'quantity': quantity,
            'sl_order_id': sl_order_id,
            'sl_trigger': initial_sl_trigger,
            'first_target_hit': False
        }
        save_state(self.state, config.STATE_FILE)
        
        # Start WebSocket if not already running
        if not self.market_ws:
            logging.info("🚀 Starting WebSocket for position monitoring...")
            self.start_market_websocket()
        
        # Subscribe to market data
        self.subscribe_to_symbol(symbol)
    
    def subscribe_to_symbol(self, symbol: str):
        """Subscribe to market data for a symbol"""
        if not self.market_ws:
            logging.warning(f"⚠️  WebSocket not available for {symbol} - will start when connection is established")
            return
            
        instrument_token = self.get_instrument_token(symbol)
        if not instrument_token:
            logging.error(f"Could not get instrument token for {symbol}")
            return
            
        if instrument_token not in self.subscribed_tokens:
            try:
                self.market_ws.subscribe([instrument_token])
                self.market_ws.set_mode(self.market_ws.MODE_LTP, [instrument_token])
                self.subscribed_tokens.add(instrument_token)
                logging.info(f"📈 Subscribed to market data for {symbol} (token: {instrument_token})")
            except Exception as e:
                logging.error(f"Failed to subscribe to {symbol}: {e}")
                if "403" in str(e) or "Forbidden" in str(e):
                    logging.error("💡 Market data access restricted - this is normal during market closure")
    
    def handle_order_update(self, order):
        """Handle order update from polling or postback"""
        try:
            status = order.get('status')
            transaction_type = order.get('transaction_type')
            symbol = order.get('tradingsymbol')
            order_type = order.get('order_type', '')
            
            # Only process BUY orders that are COMPLETE
            if (status == 'COMPLETE' and 
                transaction_type == 'BUY' and 
                order_type in ['MARKET', 'LIMIT'] and  # Not SL orders
                symbol and 
                symbol not in self.active_positions):
                
                buy_price = float(order.get('average_price', 0))
                quantity = int(order.get('filled_quantity', 0))
                
                if buy_price > 0 and quantity > 0:
                    logging.info(f"New BUY execution detected: {symbol} @ {buy_price} qty={quantity}")
                    self.start_trailing_for_position(symbol, buy_price, quantity)
                    
        except Exception as e:
            logging.error(f"Error processing order update: {e}")
    
    def handle_market_tick(self, tick):
        """Handle market data tick"""
        try:
            instrument_token = tick.get('instrument_token')
            ltp = tick.get('last_price') or tick.get('ltp')
            
            if not ltp:
                return
                
            ltp = float(ltp)
            
            # Find which symbol this tick belongs to
            for symbol, position in self.active_positions.items():
                symbol_token = self.get_instrument_token(symbol)
                if symbol_token == instrument_token:
                    self.process_price_update(symbol, position, ltp)
                    break
                    
        except Exception as e:
            logging.error(f"Error processing market tick: {e}")
    
    def process_price_update(self, symbol: str, position: dict, ltp: float):
        """Process price update for a position"""
        buy_price = position['buy_price']
        target_gap = position['target_gap']
        trail_step = position['trail_step']
        trailing_sl = position['trailing_sl']
        
        first_target = buy_price + target_gap
        
        # Check if first target hit
        if not position['first_target_hit'] and ltp >= first_target:
            position['first_target_hit'] = True
            
            if config.FIRST_TARGET_SL_MODE == "BUY":
                new_sl = buy_price
            else:
                new_sl = (buy_price + first_target) / 2.0
                
            logging.info(f"{symbol}: First target hit (LTP={ltp:.2f}). Updating SL -> {new_sl:.2f}")
            
            try:
                trailing_sl.modify_sl(new_sl)
                position['sl_trigger'] = new_sl
                
                # Update persistent state
                if symbol in self.state.get('active_positions', {}):
                    self.state['active_positions'][symbol]['first_target_hit'] = True
                    self.state['active_positions'][symbol]['sl_trigger'] = new_sl
                    save_state(self.state, config.STATE_FILE)
                    
            except Exception as e:
                logging.error(f"Failed to modify SL for {symbol}: {e}")
            return
        
        # Trailing mode after first target
        if position['first_target_hit'] and ltp > first_target:
            if config.FIRST_TARGET_SL_MODE == "BUY":
                base_sl = buy_price
            else:
                base_sl = (buy_price + first_target) / 2.0
                
            new_sl = trailing_steps(base_sl, ltp, first_target, trail_step)
            current_sl = position['sl_trigger']
            
            if new_sl > current_sl + config.MIN_SL_STEP:
                logging.info(f"{symbol}: Trailing SL update: LTP={ltp:.2f} new SL={new_sl:.4f} current SL={current_sl:.4f}")
                try:
                    trailing_sl.modify_sl(new_sl)
                    position['sl_trigger'] = new_sl
                    
                    # Update persistent state
                    if symbol in self.state.get('active_positions', {}):
                        self.state['active_positions'][symbol]['sl_trigger'] = new_sl
                        save_state(self.state, config.STATE_FILE)
                        
                except Exception as e:
                    logging.error(f"Failed to modify trailing SL for {symbol}: {e}")
    
    def start_market_websocket(self):
        """Start market data websocket"""
        try:
            # Only start if we have positions to monitor
            if not self.active_positions:
                logging.info("⏸️  No active positions - WebSocket will start when needed")
                return
                
            self.market_ws = KiteTicker(self.kite_client.kite.api_key, self.kite_client.kite.access_token)
            
            def on_ticks(ws, ticks):
                for tick in ticks:
                    self.handle_market_tick(tick)
            
            def on_connect(ws, response):
                logging.info("📡 Market data websocket connected")
                # Resubscribe to existing positions
                for symbol in self.active_positions.keys():
                    self.subscribe_to_symbol(symbol)
            
            def on_error(ws, code, reason):
                logging.error(f"WebSocket error: {code} - {reason}")
                if code == 403:
                    logging.error("🚫 WebSocket access forbidden - check token permissions")
                    logging.error("💡 This might happen during market close or with insufficient permissions")
            
            def on_close(ws, code, reason):
                logging.info(f"📡 WebSocket closed: {code} - {reason}")
                if code == 403:
                    logging.error("🚫 WebSocket connection rejected (403 Forbidden)")
                    logging.error("🕐 This usually happens when:")
                    logging.error("   • Markets are closed")
                    logging.error("   • Token doesn't have websocket permissions") 
                    logging.error("   • Rate limiting is active")
                    logging.info("⏸️  WebSocket will retry when positions are active")
                    return  # Don't auto-reconnect on 403
                
                # Auto-reconnect for other errors (not 403)
                if self.active_positions:  # Only reconnect if we have positions
                    time.sleep(10)  # Longer delay to avoid rate limiting
                    logging.info("🔄 Attempting to reconnect WebSocket...")
                    self.start_market_websocket()
            
            self.market_ws.on_ticks = on_ticks
            self.market_ws.on_connect = on_connect
            self.market_ws.on_error = on_error
            self.market_ws.on_close = on_close
            
            logging.info("🔗 Starting market data websocket...")
            self.market_ws.connect(threaded=True)
            
        except Exception as e:
            logging.error(f"❌ Failed to start market websocket: {e}")
            if "403" in str(e) or "Forbidden" in str(e):
                logging.error("💡 WebSocket access forbidden - this is normal during market closure")
    
    def restore_positions(self):
        """Restore positions from saved state"""
        saved_positions = self.state.get('active_positions', {})
        
        for symbol, pos_data in saved_positions.items():
            logging.info(f"Restoring position for {symbol}")
            
            # Check if position still exists
            try:
                positions = self.kite_client.get_positions()
                position_exists = False
                
                for position in positions.get("day", []):
                    if (position.get("tradingsymbol") == symbol and 
                        float(position.get("quantity", 0)) > 0):
                        position_exists = True
                        break
                
                if position_exists:
                    # Recreate the position info
                    buy_price = pos_data['buy_price']
                    quantity = pos_data['quantity']
                    
                    # Calculate gaps
                    lots = max(1, quantity // 75)
                    sl_gap = money_to_points(config.RISK_RUPEES, quantity, lots, config.RISK_MODE)
                    target_gap = money_to_points(config.REWARD_RUPEES, quantity, lots, config.RISK_MODE)
                    trail_step = money_to_points(config.TRAIL_RUPEES, quantity, lots, config.RISK_MODE)
                    
                    position_state = {
                        'buy_price': buy_price,
                        'position_qty': quantity,
                        'first_target_hit': pos_data.get('first_target_hit', False),
                        'sl_order_id': pos_data.get('sl_order_id'),
                        'sl_trigger': pos_data.get('sl_trigger', 0.0)
                    }
                    
                    position_info = {
                        'symbol': symbol,
                        'buy_price': buy_price,
                        'quantity': quantity,
                        'sl_gap': sl_gap,
                        'target_gap': target_gap,
                        'trail_step': trail_step,
                        'first_target_hit': pos_data.get('first_target_hit', False),
                        'sl_order_id': pos_data.get('sl_order_id'),
                        'sl_trigger': pos_data.get('sl_trigger', 0.0),
                        'trailing_sl': TrailingSL(self.kite_client, symbol, quantity, config, position_state)
                    }
                    
                    self.active_positions[symbol] = position_info
                    self.subscribe_to_symbol(symbol)
                    logging.info(f"Position restored for {symbol}")
                else:
                    # Position closed, remove from state
                    logging.info(f"Position {symbol} no longer exists, removing from state")
                    
            except Exception as e:
                logging.error(f"Error restoring position {symbol}: {e}")
    
    def run(self):
        """Main run method - Postback mode only"""
        logging.info("🚀 Starting Dynamic Trading Bot (Postback Mode)...")
        
        # Restore any existing positions
        self.restore_positions()
        
        # Only start websocket if we have active positions
        if self.active_positions:
            logging.info("📍 Found existing positions - starting WebSocket...")
            self.start_market_websocket()
        else:
            logging.info("📡 WebSocket will start automatically when positions are detected")
        
        # Bot is now ready to receive postback notifications
        logging.info("✅ Bot is ready! Waiting for postback notifications...")
        logging.info("📡 Orders will be detected via postback URL automatically")
        logging.info("🔧 Make sure your postback URL is configured in Zerodha app settings")
        
        try:
            while True:
                # Just keep the bot alive for websocket and postback handling
                time.sleep(30)  # Check every 30 seconds if everything is still running
                
                # Log status occasionally
                active_count = len(self.active_positions)
                if active_count > 0:
                    logging.info(f"📊 Bot monitoring {active_count} active positions")
                
        except KeyboardInterrupt:
            logging.info("⏹️  Bot stopped by user")
        except Exception as e:
            logging.error(f"❌ Bot error: {e}")
        finally:
            if self.market_ws:
                try:
                    self.market_ws.close()
                    logging.info("🔌 Market websocket closed")
                except:
                    pass

# Only class-based approach needed for postback integration
if __name__ == "__main__":
    # For direct testing only
    print("⚠️  This file should be imported, not run directly.")
    print("✅ Use: pdm run python scripts/run_with_postback.py")
    print("📡 This starts the integrated postback server with the bot.")
