import time
import queue
import logging
from config import INSTRUMENT_TOKENS
from data_feed import DataFeed, fetch_nifty_option_tokens
from processing import ProcessingEngine
from signal_engine import SignalEngine

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    logging.info("Starting Zerodha Signal Engine...")
    
    # 1. Fetch Option Tokens dynamically
    option_tokens = fetch_nifty_option_tokens()
    
    # Combine standard tokens (like NIFTY Spot 256265) with option tokens
    all_tokens = INSTRUMENT_TOKENS + option_tokens
    logging.info(f"Total tokens to subscribe: {len(all_tokens)}")
    
    # 2. Initialize Thread-safe Queue
    tick_queue = queue.Queue()
    
    # 3. Shared Data Store
    latest_data = {}
    
    # 4. Initialize Engines
    data_feed = DataFeed(tick_queue, instrument_tokens=all_tokens)
    processing_engine = ProcessingEngine(tick_queue, latest_data)
    signal_engine = SignalEngine()
    
    # 5. Start Threads
    processing_engine.start()
    data_feed.start()
    
    try:
        while True:
            time.sleep(5)
            # Dump minimal log instead of whole dictionary
            logging.info(f"Processing running... Tracked instruments: {len(latest_data)}")
    except KeyboardInterrupt:
        logging.info("Stopping...")
        data_feed.stop()
        processing_engine.stop()
        logging.info("Stopped successfully.")
