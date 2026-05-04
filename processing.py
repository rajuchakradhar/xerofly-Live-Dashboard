import threading
import time
import json
import logging
from signal_engine import SignalEngine

class ProcessingEngine:
    def __init__(self, tick_queue, latest_data):
        self.tick_queue = tick_queue
        self.latest_data = latest_data # Shared dictionary
        self.running = False
        self.signal_engine = SignalEngine()
        
    def process_tick(self, tick):
        token = tick.get("instrument_token")
        
        if token not in self.latest_data:
            self.latest_data[token] = {}
            
        self.latest_data[token]['ltp'] = tick.get('last_price')
        self.latest_data[token]['volume'] = tick.get('volume_traded')
        self.latest_data[token]['ltq'] = tick.get('last_traded_quantity', 0)
        
        # Check if it is an option to calculate IV
        if tick.get("is_option"):
            # We assume spot price is from NIFTY token (256265)
            spot = self.latest_data.get(256265, {}).get("ltp", 22430)
            signals = self.signal_engine.evaluate(
                tick, 
                spot_price=spot,
                strike=tick.get("strike"),
                dte=tick.get("dte"),
                option_type=tick.get("option_type")
            )
            self.latest_data[token]['iv'] = signals.get('iv', 0.0)
            self.latest_data[token]['type'] = f"OPT {tick.get('strike')} {tick.get('option_type').upper()}"
        else:
            signals = self.signal_engine.evaluate(tick)
            self.latest_data[token]['atm'] = signals.get('atm_strike')
            self.latest_data[token]['type'] = "INDEX"
            
        if signals.get('smart_money_flag'):
            self.latest_data[token]['smart_money'] = "🚨 " + signals.get('smart_money_reason')
        else:
            self.latest_data[token]['smart_money'] = "Normal"
            
        self.latest_data[token]['last_updated'] = time.time()
        
    def _run(self):
        last_save = time.time()
        while self.running:
            if not self.tick_queue.empty():
                tick = self.tick_queue.get()
                self.process_tick(tick)
            else:
                time.sleep(0.01)
                
            # Dump to JSON every 1 second for Streamlit dashboard
            if time.time() - last_save > 1.0:
                try:
                    with open("live_data.json", "w") as f:
                        json.dump(self.latest_data, f)
                except Exception as e:
                    logging.error(f"Failed to write live data: {e}")
                last_save = time.time()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        
    def stop(self):
        self.running = False
