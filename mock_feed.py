import time
import random
import queue
import threading
from processing import ProcessingEngine

# Mock data script for testing without a Kite API Key
def generate_mock_ticks(tick_queue):
    while True:
        # Normal Index Tick
        tick = {
            "instrument_token": 256265, # NIFTY 50
            "last_price": 22430.0 + random.uniform(-10, 10),
            "volume_traded": random.randint(10000, 15000),
            "last_traded_quantity": random.choice([50, 100, 250, 1500, 50]) # Occasional high LTQ for Smart Money
        }
        tick_queue.put(tick)
        
        # Normal Index Tick
        tick2 = {
            "instrument_token": 123456, # BANKNIFTY
            "last_price": 48210.0 + random.uniform(-20, 20),
            "volume_traded": random.randint(20000, 28000),
            "last_traded_quantity": random.choice([15, 30, 45, 1200, 15])
        }
        tick_queue.put(tick2)
        
        # Option Tick (NIFTY 22400 CE)
        # Spot is around ~22430. Call option is In-The-Money.
        tick_opt = {
            "instrument_token": 999999, # NIFTY 22400 CE
            "last_price": 120.0 + random.uniform(-2, 2), # Mock option premium
            "volume_traded": random.randint(50000, 60000),
            "last_traded_quantity": random.choice([50, 200, 50]),
            "is_option": True,
            "strike": 22400,
            "option_type": "c",
            "dte": 3 # 3 days to expiry
        }
        tick_queue.put(tick_opt)
        
        time.sleep(0.5)

if __name__ == "__main__":
    print("Starting Mock Feed Engine...")
    tick_queue = queue.Queue()
    latest_data = {}
    
    processing_engine = ProcessingEngine(tick_queue, latest_data)
    processing_engine.start()
    
    mock_thread = threading.Thread(target=generate_mock_ticks, args=(tick_queue,), daemon=True)
    mock_thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping mock feed...")
        processing_engine.stop()
