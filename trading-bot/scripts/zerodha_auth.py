#!/usr/bin/env python3
"""
Zerodha Authentication Utility
Standalone script for getting Zerodha API credentials and access tokens
"""

from src.auth import ZerodhaAuth

def main():
    """Main function to run authentication"""
    print("=== Zerodha Authentication Utility ===")
    
    auth = ZerodhaAuth()
    credentials = auth.authenticate()
    
    print("\n=== Authentication Successful ===")
    print(f"API Key: {credentials['api_key']}")
    print(f"Access Token: {credentials['access_token']}")
    
    return credentials

if __name__ == "__main__":
    main()