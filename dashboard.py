import streamlit as st
import time
import json
import pandas as pd
import os

st.set_page_config(page_title="Zerodha Live Signal Dashboard", layout="wide")
st.title("📈 Live Market Signals")

def get_latest_data():
    if os.path.exists("live_data.json"):
        try:
            with open("live_data.json", "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

placeholder = st.empty()

while True:
    raw_data = get_latest_data()
    
    if raw_data:
        # Convert dict to list for dataframe
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
        
        with placeholder.container():
            st.subheader("Live Tracking Table")
            # Highlight Smart Money signals dynamically using pandas styling
            def highlight_smart_money(val):
                color = 'red' if '🚨' in str(val) else ''
                return f'color: {color}'
            
            styled_df = df.style.applymap(highlight_smart_money, subset=['Smart Money Signal'])
            st.dataframe(styled_df, use_container_width=True)
    else:
        with placeholder.container():
            st.warning("Waiting for live data... (Ensure main.py or mock_feed.py is running)")
            
    time.sleep(1)
