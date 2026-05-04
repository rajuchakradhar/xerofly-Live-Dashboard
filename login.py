import os
from kiteconnect import KiteConnect
from config import KITE_API_KEY, KITE_API_SECRET

def login():
    if not KITE_API_KEY or KITE_API_KEY == "your_api_key_here":
        print("Please set your KITE_API_KEY and KITE_API_SECRET in config.py first.")
        return

    kite = KiteConnect(api_key=KITE_API_KEY)
    
    print("=========================================")
    print("ZERODHA LOGIN FLOW")
    print("=========================================\n")
    print("1. Click or copy this URL into your browser:")
    print(f"   {kite.login_url()}\n")
    print("2. Log in with your Zerodha credentials (and TOTP).")
    print("3. You will be redirected to your Redirect URL.")
    print("4. Copy the 'request_token' from the address bar (it is the long text after '?request_token=').")
    
    request_token = input("\nPaste the request_token here: ").strip()
    
    if not request_token:
        print("No request token provided. Exiting.")
        return
        
    try:
        print("\nGenerating access token...")
        data = kite.generate_session(request_token, api_secret=KITE_API_SECRET)
        access_token = data["access_token"]
        print("\nSUCCESS!")
        print("Your Access Token is:")
        print(f"\n{access_token}\n")
        print("Please paste this access token into KITE_ACCESS_TOKEN in config.py.")
        print("After that, you can run `python main.py` to start the live feed!")
    except Exception as e:
        print(f"\nLogin failed: {e}")
        print("Ensure your API Secret is correct and the request_token hasn't expired.")

if __name__ == "__main__":
    login()
