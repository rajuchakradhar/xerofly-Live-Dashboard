import streamlit as st
import time
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Zerodha Live Signal Dashboard", layout="wide")
st.title("📈 Live Market Signals")

@st.cache_data(ttl=900) # Cache data for 15 minutes (900 seconds)
def get_latest_data():
    try:
        ticker = yf.Ticker("^NSEI")
        data = ticker.history(period="1d")
        if not data.empty:
            last_price = float(data['Close'].iloc[-1])
            volume = int(data['Volume'].iloc[-1])
            return {
                "256265": {
                    "type": "INDEX",
                    "ltp": last_price,
                    "atm": round(last_price / 50) * 50,
                    "iv": "-",
                    "ltq": 0,
                    "volume": volume,
                    "smart_money": "Normal"
                }
            }
    except Exception as e:
        st.error(f"Error fetching data: {e}")
    return {}

import requests
import json

@st.cache_data(ttl=60)
def fetch_nse_option_chain():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        session.get('https://www.nseindia.com', timeout=10)
        time.sleep(1) # wait a moment to set cookies
        
        url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
        session.headers.update({'Referer': 'https://www.nseindia.com/get-quote/optionchain?symbol=NIFTY'})
        
        response = session.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'records' in data and 'data' in data['records']:
                return data['records']['data']
            else:
                return f"Error: Unexpected JSON format. Keys: {list(data.keys())}"
        else:
            return f"HTTP {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return str(e)

raw_data = get_latest_data()

st.subheader("Live Tracking Table (Nifty 50 Spot)")
if raw_data:
    table_data = []
    for token, details in raw_data.items():
        table_data.append({
            "Token": token,
            "Type": details.get("type", "UNKNOWN"),
            "LTP": round(details.get("ltp", 0), 2),
            "ATM Strike": details.get("atm", "-"),
            "Implied Volatility (%)": details.get("iv", "-"),
            "Last Traded Qty (LTQ)": details.get("ltq", 0),
            "Total Volume": details.get("volume", 0),
            "Smart Money Signal": details.get("smart_money", "Normal")
        })
    df = pd.DataFrame(table_data)
    
    def highlight_smart_money(val):
        color = 'red' if '🚨' in str(val) else ''
        return f'color: {color}'
    
    styled_df = df.style.map(highlight_smart_money, subset=['Smart Money Signal'])
    st.dataframe(styled_df, use_container_width=True)
else:
    st.warning("Waiting for live data...")

st.markdown("---")
st.subheader("Experimental: NSE Option Chain Fetcher")
st.write("Clicking this will attempt to fetch the latest Nifty Option Chain directly from NSE. **Note:** This may fail on Streamlit Cloud due to NSE bot protection.")

if st.button("Fetch NSE Option Chain (Once)"):
    with st.spinner("Attempting to connect to NSE..."):
        result = fetch_nse_option_chain()
        if isinstance(result, list):
            st.success(f"Successfully fetched {len(result)} strikes from NSE!")
            
            # Format option chain for display
            oc_data = []
            for item in result:
                ce = item.get('CE', {})
                pe = item.get('PE', {})
                oc_data.append({
                    "CE Open Interest": ce.get('openInterest', 0),
                    "CE LTP": ce.get('lastPrice', 0),
                    "Strike": item.get('strikePrice', 0),
                    "PE LTP": pe.get('lastPrice', 0),
                    "PE Open Interest": pe.get('openInterest', 0),
                    "Expiry": item.get('expiryDate', '')
                })
                
            oc_df = pd.DataFrame(oc_data)
            st.dataframe(oc_df)
        else:
            st.error(f"Failed to fetch Option Chain. NSE Blocked the Request.\n\nReason: {result}")
