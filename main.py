import time
import queue
import logging
from periodic_feed import PeriodicFeed
from processing import ProcessingEngine
from signal_engine import SignalEngine

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    logging.info("Starting Zerodha Signal Engine...")
    
    # 1. Initialize Thread-safe Queue
    tick_queue = queue.Queue()
    
    # 2. Shared Data Store
    latest_data = {}
    
    # 3. Initialize Engines
    data_feed = PeriodicFeed(tick_queue, interval_minutes=15)
    processing_engine = ProcessingEngine(tick_queue, latest_data)
    signal_engine = SignalEngine()
    
    # 4. Start Threads
    processing_engine.start()
    data_feed.start()
    
    try:
        while True:
            time.sleep(5)
            logging.info(f"Latest Data Snapshot: {latest_data}")
    except KeyboardInterrupt:
        logging.info("Stopping...")
        data_feed.stop()
        processing_engine.stop()
        logging.info("Stopped successfully.")
