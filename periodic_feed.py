import logging
import time
import threading
import schedule
import yfinance as yf

class PeriodicFeed:
    def __init__(self, tick_queue, interval_minutes=15):
        self.tick_queue = tick_queue
        self.interval_minutes = interval_minutes
        self.running = False
        self.thread = None

    def fetch_data(self):
        logging.info("Fetching Nifty 50 data from yfinance...")
        try:
            # ^NSEI is the ticker for Nifty 50 on Yahoo Finance
            ticker = yf.Ticker("^NSEI")
            data = ticker.history(period="1d")
            
            if not data.empty:
                last_price = float(data['Close'].iloc[-1])
                volume = int(data['Volume'].iloc[-1])
                
                # Format tick for processing engine
                tick = {
                    "instrument_token": 256265,  # Matches the Nifty 50 token in config.py
                    "last_price": last_price,
                    "volume_traded": volume,
                    "last_traded_quantity": 0, # Not provided by yfinance
                    "is_option": False
                }
                
                self.tick_queue.put(tick)
                logging.info(f"Pushed new Nifty 50 tick: LTP={last_price}, Vol={volume}")
            else:
                logging.warning("No data returned from yfinance for ^NSEI")
        except Exception as e:
            logging.error(f"Error fetching data from yfinance: {e}")

    def run_scheduler(self):
        # Fetch immediately on start
        self.fetch_data()
        
        # Schedule to run every X minutes
        schedule.every(self.interval_minutes).minutes.do(self.fetch_data)
        
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.thread.start()
        logging.info(f"Periodic feed started. Fetching every {self.interval_minutes} minutes.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        logging.info("Periodic feed stopped.")
