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
from src.bot import DynamicTradingBot

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Global bot instance (in production, use proper singleton pattern)
bot_instance = None

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
    global bot_instance
    
    print("🚀 Starting Dynamic Trading Bot...")
    print("📡 Integrated with real-time postback notifications!")
    print("\n🔧 POSTBACK SETUP:")
    print("1. Configure this URL in your Zerodha app postback settings:")
    print("   📍 Production: https://yourdomain.com/postback")
    print("   📍 Local: https://your-ngrok-url.ngrok.io/postback")
    print("\n💡 For local testing:")
    print("   📱 Run: ngrok http 5001")
    print("   📍 Then use the ngrok HTTPS URL in Zerodha settings")
    print("\n✅ Once configured, you'll get INSTANT order notifications!")
    print("📈 Just place your orders in Kite - bot handles the rest!")
    print("⏹️  Press Ctrl+C to stop everything.\n")
    
    # Start the bot in a separate thread
    import threading
    bot_instance = DynamicTradingBot()
    bot_thread = threading.Thread(target=bot_instance.run, daemon=True)
    bot_thread.start()
    
    print("🤖 Trading bot started and ready...")
    print("🌐 Flask postback server starting on port 5001...")
    
    # Run Flask server on port 5001 to avoid macOS AirPlay conflict
    app.run(host='0.0.0.0', port=5001, debug=False)

if __name__ == "__main__":
    run_postback_server()