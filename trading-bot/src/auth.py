import os
import sys
import json
import datetime
from kiteconnect import KiteConnect
from . import config


class ZerodhaAuth:
    """Handle Zerodha authentication and token management"""
    
    def __init__(self):
        self.login_credential = None
        self.access_token = None
    
    def _update_env_file(self, access_token, token_date):
        """Update the .env file with new access token and date"""
        # Get the absolute path to the .env file (in the trading-bot directory)
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_file = os.path.join(current_dir, ".env")
        
        print(f"Looking for .env file at: {env_file}")
        
        if not os.path.exists(env_file):
            print(f"Warning: .env file not found at {env_file}!")
            return
            
        # Read current .env content
        with open(env_file, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Update or add ACCESS_TOKEN and ACCESS_TOKEN_DATE
        token_updated = False
        date_updated = False
        
        for i, line in enumerate(lines):
            if line.startswith('ACCESS_TOKEN='):
                lines[i] = f'ACCESS_TOKEN={access_token}'
                token_updated = True
                print(f"Updated ACCESS_TOKEN in line {i+1}")
            elif line.startswith('ACCESS_TOKEN_DATE='):
                lines[i] = f'ACCESS_TOKEN_DATE={token_date}'
                date_updated = True
                print(f"Updated ACCESS_TOKEN_DATE in line {i+1}")
        
        # Add new lines if not found
        if not token_updated:
            # Find where to insert (after API_SECRET)
            for i, line in enumerate(lines):
                if line.startswith('API_SECRET='):
                    lines.insert(i + 1, f'ACCESS_TOKEN={access_token}')
                    print(f"Added ACCESS_TOKEN after line {i+1}")
                    break
        
        if not date_updated:
            # Find where to insert (after ACCESS_TOKEN)
            for i, line in enumerate(lines):
                if line.startswith('ACCESS_TOKEN='):
                    lines.insert(i + 1, f'ACCESS_TOKEN_DATE={token_date}')
                    print(f"Added ACCESS_TOKEN_DATE after line {i+1}")
                    break
        
        # Write back to file
        with open(env_file, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ Access token saved to .env file (valid until {token_date})")
    
    def _is_token_valid(self):
        """Check if stored access token is still valid (same day)"""
        # Reload config to get latest .env values
        from . import config
        from importlib import reload
        reload(config)
        
        if not config.ACCESS_TOKEN or not config.ACCESS_TOKEN_DATE:
            return False
            
        try:
            token_date = datetime.datetime.strptime(config.ACCESS_TOKEN_DATE, '%Y-%m-%d').date()
            today = datetime.datetime.now().date()
            return token_date >= today
        except (ValueError, TypeError):
            return False
        
    def _load_credentials(self):
        """Load login credentials from .env configuration"""
        if config.API_KEY and config.API_SECRET:
            print("Loading credentials from configuration...")
            self.login_credential = {
                "api_key": config.API_KEY,
                "api_secret": config.API_SECRET
            }
            return
        
        # Fallback: prompt user if not in .env
        print("---- Enter your Zerodha Login Credentials ----")
        print("(Tip: Set API_KEY and API_SECRET in .env file to avoid this prompt)")
        self.login_credential = {
            "api_key": str(input("Enter API Key: ")),
            "api_secret": str(input("Enter API Secret: "))
        }
        print("Consider adding these credentials to your .env file for automatic loading.")
    
    def _get_access_token(self):
        """Get access token from .env file or generate new one"""
        # Check if we have a valid token in .env
        if self._is_token_valid():
            print("✅ Using existing valid access token from .env file")
            self.access_token = config.ACCESS_TOKEN
            return
        
        # Generate new token
        print("🔐 Generating new access token...")
        print("Trying Log In...")
        kite = KiteConnect(api_key=self.login_credential["api_key"])
        print("Login url : ", kite.login_url())
        request_tkn = input("Login and enter your 'request token' here : ")
        
        try:
            self.access_token = kite.generate_session(
                request_token=request_tkn, 
                api_secret=self.login_credential["api_secret"]
            )['access_token']
            
            # Save to .env file
            today_str = datetime.datetime.now().date().strftime('%Y-%m-%d')
            self._update_env_file(self.access_token, today_str)
            
            print("Login successful...")
        except Exception as e:
            print(f"Login Failed {{{e}}}")
            sys.exit()
    
    def authenticate(self):
        """Main authentication method"""
        print("---Getting Access Token---")
        self._load_credentials()
        self._get_access_token()
        
        if config.ACCESS_TOKEN and config.ACCESS_TOKEN_DATE:
            token_date = config.ACCESS_TOKEN_DATE
            print(f"🔑 Using access token (valid until {token_date})")
        else:
            print(f"🔑 Access token: {self.access_token[:20]}..." if len(self.access_token) > 20 else self.access_token)
        
        return {
            "api_key": self.login_credential["api_key"],
            "access_token": self.access_token
        }
    
    def get_credentials(self):
        """Get credentials without re-authentication if already loaded"""
        if not self.login_credential or not self.access_token:
            return self.authenticate()
        
        return {
            "api_key": self.login_credential["api_key"],
            "access_token": self.access_token
        }


def main():
    """Standalone script functionality"""
    try:
        from kiteconnect import KiteConnect
    except ImportError:
        os.system('python -m pip install kiteconnect')
    
    auth = ZerodhaAuth()
    credentials = auth.authenticate()
    return credentials


if __name__ == "__main__":
    main()