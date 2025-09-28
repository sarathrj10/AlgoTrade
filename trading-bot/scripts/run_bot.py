"""
Dynamic Trading Bot - Main Entry Point

This is the ONLY way to run the bot. It provides:
- Real-time order detection via HTTP postback (0ms delay)
- Integrated Flask server to receive Zerodha notifications  
- Automatic trailing SL management for detected positions
- Complete authentication handling via Zerodha auth

Usage: pdm run python scripts/run_bot.py

Setup:
1. Run this script
2. Configure postback URL in Zerodha app: https://your-server.com/postback
3. Place orders manually in Kite
4. Bot automatically handles trailing SL in real-time
"""

import sys
import os
# Add the trading-bot directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
import json
import logging
import threading
import signal
import atexit
from src.bot import DynamicTradingBot
from src import config

# Optional ngrok import
ngrok = None
if config.USE_NGROK:
    try:
        from pyngrok import ngrok
        logging.info("✅ pyngrok imported successfully")
    except ImportError:
        logging.warning("⚠️  pyngrok not installed. Install with: pip install pyngrok")
        logging.warning("⚠️  Continuing without ngrok support...")
        config.USE_NGROK = False

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Global bot instance (in production, use proper singleton pattern)
bot_instance = None
ngrok_tunnel = None
shutdown_event = threading.Event()

def cleanup():
    """Clean up resources on exit"""
    global ngrok_tunnel, bot_instance
    
    # Set shutdown event to stop any running threads gracefully
    shutdown_event.set()
    
    # Clean up ngrok tunnel
    if ngrok_tunnel:
        try:
            ngrok.disconnect(ngrok_tunnel.public_url)
            print("🔌 Ngrok tunnel disconnected")
        except:
            pass
    
    # Clean up bot instance
    if bot_instance and hasattr(bot_instance, 'market_ws') and bot_instance.market_ws:
        try:
            bot_instance.market_ws.close()
        except:
            pass
    
    # Ensure logging is properly flushed
    logging.shutdown()

def signal_handler(signum, frame):
    """Handle system signals gracefully"""
    print(f"\n⏹️  Received signal {signum}, shutting down gracefully...")
    cleanup()
    sys.exit(0)

# Register signal handlers and cleanup
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
atexit.register(cleanup)

@app.route('/postback', methods=['POST'])
def handle_postback():
    """Handle postback from Zerodha"""
    try:
        # Get the postback data
        data = request.get_json()
        
        if not data:
            # Sometimes data comes as form data
            data = request.form.to_dict()
        
        logging.info(f"Received postback: {data}")
        
        # Forward to bot if available
        if bot_instance:
            bot_instance.handle_order_update(data)
        
        return jsonify({"status": "success"})
        
    except Exception as e:
        logging.error(f"Error handling postback: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Postback server is running"})

def run_postback_server():
    """Run the integrated bot with postback server"""
    global bot_instance, ngrok_tunnel
    
    print("🚀 Starting Dynamic Trading Bot...")
    print("📡 Integrated with real-time postback notifications!")
    
    # Start ngrok tunnel if enabled
    if config.USE_NGROK and ngrok:
        try:
            # Set auth token if provided
            if config.NGROK_AUTH_TOKEN:
                ngrok.set_auth_token(config.NGROK_AUTH_TOKEN)
            
            # Create tunnel
            ngrok_tunnel = ngrok.connect(5001)
            public_url = ngrok_tunnel.public_url
            
            print(f"\n🌐 NGROK TUNNEL CREATED:")
            print(f"   📍 Public URL: {public_url}")
            print(f"   � Postback URL: {public_url}/postback")
            print(f"   📍 Health check: {public_url}/health")
            
        except Exception as e:
            logging.error(f"❌ Failed to create ngrok tunnel: {e}")
            print("⚠️  Continuing without ngrok tunnel...")
    
    print("\n�🔧 POSTBACK SETUP:")
    if ngrok_tunnel:
        print("✅ NGROK ENABLED - Use this URL in Zerodha app:")
        print(f"   📍 {ngrok_tunnel.public_url}/postback")
    else:
        print("1. Configure this URL in your Zerodha app postback settings:")
        print("   📍 Production: https://yourdomain.com/postback")
        print("   📍 Local: https://your-ngrok-url.ngrok.io/postback")
        print("\n💡 For local testing:")
        print("   📱 Run: ngrok http 5001")
        print("   📍 Or set USE_NGROK=true in .env for automatic tunnel")
    
    print("\n✅ Once configured, you'll get INSTANT order notifications!")
    print("📈 Just place your orders in Kite - bot handles the rest!")
    print("⏹️  Press Ctrl+C to stop everything.\n")
    
    # Start the bot in a separate thread
    bot_instance = DynamicTradingBot()
    bot_thread = threading.Thread(target=bot_instance.run, daemon=True)
    bot_thread.start()
    
    print("🤖 Trading bot started and ready...")
    print("🌐 Flask postback server starting on port 5001...")
    
    try:
        # Run Flask server on port 5001 to avoid macOS AirPlay conflict
        app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
    except (KeyboardInterrupt, SystemExit):
        print("\n⏹️  Shutting down...")
    except Exception as e:
        logging.error(f"Server error: {e}")
    finally:
        # cleanup() will be called automatically via atexit
        pass

if __name__ == "__main__":
    run_postback_server()