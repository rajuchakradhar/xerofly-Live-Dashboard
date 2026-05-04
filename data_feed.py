import logging
import pandas as pd
import requests
import io
from kiteconnect import KiteTicker
from config import KITE_API_KEY, KITE_ACCESS_TOKEN

def fetch_nifty_option_tokens():
    """
    Downloads the daily instruments list from Zerodha, filters for NIFTY options
    of the nearest expiry, and returns a list of their instrument tokens.
    """
    logging.info("Downloading latest instruments list from Kite API...")
    url = "https://api.kite.trade/instruments"
    r = requests.get(url)
    df = pd.read_csv(io.StringIO(r.text))
    
    # Filter for NIFTY options
    nifty_opts = df[(df['name'] == 'NIFTY') & (df['instrument_type'].isin(['CE', 'PE']))]
    
    if nifty_opts.empty:
        logging.warning("No NIFTY options found in the instrument list!")
        return []
        
    # Sort by expiry to find current expiry
    expiries = sorted(nifty_opts['expiry'].unique())
    current_expiry = expiries[0]
    
    current_opts = nifty_opts[nifty_opts['expiry'] == current_expiry]
    tokens = current_opts['instrument_token'].tolist()
    
    logging.info(f"Found {len(tokens)} NIFTY option tokens for expiry {current_expiry}")
    return tokens

class DataFeed:
    def __init__(self, tick_queue, instrument_tokens):
        self.kws = KiteTicker(KITE_API_KEY, KITE_ACCESS_TOKEN)
        self.tick_queue = tick_queue
        self.instrument_tokens = instrument_tokens
        
        # Assign callbacks
        self.kws.on_ticks = self.on_ticks
        self.kws.on_connect = self.on_connect
        self.kws.on_close = self.on_close
        self.kws.on_error = self.on_error

    def on_ticks(self, ws, ticks):
        # Push ticks to the queue for the processing engine
        for tick in ticks:
            self.tick_queue.put(tick)

    def on_connect(self, ws, response):
        logging.info(f"Successfully connected to Kite WebSocket. Subscribing to {len(self.instrument_tokens)} tokens...")
        # Note: Kite allows max 3000 tokens per websocket. We are safe with ~200 NIFTY options.
        ws.subscribe(self.instrument_tokens)
        ws.set_mode(ws.MODE_FULL, self.instrument_tokens)

    def on_close(self, ws, code, reason):
        logging.warning(f"WebSocket closed: {code} - {reason}")

    def on_error(self, ws, code, reason):
        logging.error(f"WebSocket error: {code} - {reason}")

    def start(self):
        # threaded=True runs the websocket in a background thread
        self.kws.connect(threaded=True)
        
    def stop(self):
        self.kws.close()
