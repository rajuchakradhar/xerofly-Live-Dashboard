import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Zerodha Live Option Chain", layout="wide")
st.title("📈 Live Option Chain (Zerodha)")

def get_latest_data():
    if os.path.exists("live_data.json"):
        try:
            with open("live_data.json", "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

@st.fragment(run_every="1s")
def live_option_chain():
    raw_data = get_latest_data()
    
    if not raw_data:
        st.warning("Waiting for live data from main.py...")
        return
        
    # Split data into Spot and Options
    spot_data = None
    options_data = []
    
    for token, details in raw_data.items():
        if str(token) == "256265" or details.get("type") == "INDEX":
            spot_data = details
        elif "OPT" in str(details.get("type", "")):
            options_data.append(details)
            
    # Show Spot Price
    if spot_data:
        st.subheader(f"NIFTY 50 Spot: {round(spot_data.get('ltp', 0), 2)}")
        
    if not options_data:
        st.info("No option data streaming yet. Waiting for WebSocket...")
        return
        
    # Build Option Chain Table
    # We will format it like a traditional option chain: CE on left, PE on right, Strike in middle
    strikes = {}
    
    for opt in options_data:
        # type looks like "OPT 24000 C"
        parts = opt.get("type", "").split()
        if len(parts) >= 3:
            strike = int(float(parts[1]))
            opt_type = parts[2]
            
            if strike not in strikes:
                strikes[strike] = {"Strike": strike}
                
            if opt_type == "C" or opt_type == "CE":
                strikes[strike]["CE LTP"] = round(opt.get("ltp", 0), 2)
                strikes[strike]["CE Vol"] = opt.get("volume", 0)
                strikes[strike]["CE IV"] = opt.get("iv", 0)
                strikes[strike]["CE Signal"] = opt.get("smart_money", "Normal")
            else:
                strikes[strike]["PE LTP"] = round(opt.get("ltp", 0), 2)
                strikes[strike]["PE Vol"] = opt.get("volume", 0)
                strikes[strike]["PE IV"] = opt.get("iv", 0)
                strikes[strike]["PE Signal"] = opt.get("smart_money", "Normal")
                
    # Create DataFrame
    df = pd.DataFrame(list(strikes.values()))
    if not df.empty:
        df = df.sort_values("Strike").reset_index(drop=True)
        
        # Ensure all columns exist
        cols = ["CE Signal", "CE Vol", "CE IV", "CE LTP", "Strike", "PE LTP", "PE IV", "PE Vol", "PE Signal"]
        for c in cols:
            if c not in df.columns:
                df[c] = "-"
                
        df = df[cols]
        
        def highlight_signals(val):
            color = 'red' if '🚨' in str(val) else ''
            return f'color: {color}'
            
        styled_df = df.style.map(highlight_signals, subset=['CE Signal', 'PE Signal'])
        st.dataframe(styled_df, use_container_width=True, height=600)

live_option_chain()
