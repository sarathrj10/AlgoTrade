import os
import sys
import json
import datetime
from kiteconnect import KiteConnect
from . import config


class ZerodhaAuth:
    """Handle Zerodha authentication and token management"""
    
    def __init__(self, credentials_file="Login Credentials.json", token_dir="AccessToken"):
        self.credentials_file = credentials_file
        self.token_dir = token_dir
        self.login_credential = None
        self.access_token = None
        
    def _load_credentials(self):
        """Load login credentials from config, file, or prompt user"""
        # First, try to load from config (environment variables)
        if config.API_KEY and config.API_SECRET:
            print("Loading credentials from configuration...")
            self.login_credential = {
                "api_key": config.API_KEY,
                "api_secret": config.API_SECRET
            }
            return
        
        # Second, try to load from file
        try:
            with open(self.credentials_file, "r") as f:
                self.login_credential = json.load(f)
                print("Loading credentials from saved file...")
                return
        except FileNotFoundError:
            pass
        
        # Last resort: prompt user
        print("---- Enter your Zerodha Login Credentials ----")
        print("(Tip: You can set API_KEY and API_SECRET in .env file to avoid this prompt)")
        self.login_credential = {
            "api_key": str(input("Enter API Key: ")),
            "api_secret": str(input("Enter API Secret: "))
        }
        
        if input("Press Y to save login credentials to file and any key to bypass: ").upper() == "Y":
            with open(self.credentials_file, "w") as f:
                json.dump(self.login_credential, f)
            print("Credentials saved to file...")
        else:
            print("Credentials not saved. Consider setting them in .env file.")
    
    def _get_access_token(self):
        """Get access token from file or generate new one"""
        token_file = os.path.join(self.token_dir, f"{datetime.datetime.now().date()}.json")
        
        if os.path.exists(token_file):
            with open(token_file, "r") as f:
                self.access_token = json.load(f)
        else:
            print("Trying Log In...")
            kite = KiteConnect(api_key=self.login_credential["api_key"])
            print("Login url : ", kite.login_url())
            request_tkn = input("Login and enter your 'request token' here : ")
            
            try:
                self.access_token = kite.generate_session(
                    request_token=request_tkn, 
                    api_secret=self.login_credential["api_secret"]
                )['access_token']
                
                os.makedirs(self.token_dir, exist_ok=True)
                with open(token_file, "w") as f:
                    json.dump(self.access_token, f)
                print("Login successful...")
            except Exception as e:
                print(f"Login Failed {{{e}}}")
                sys.exit()
    
    def authenticate(self):
        """Main authentication method"""
        print("---Getting Access Token---")
        self._load_credentials()
        self._get_access_token()
        
        print(f"API Key : {self.login_credential['api_key']}")
        print(f"Access Token : {self.access_token}")
        
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