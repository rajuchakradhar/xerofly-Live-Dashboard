import logging
from kiteconnect import KiteTicker
from config import KITE_API_KEY, KITE_ACCESS_TOKEN, INSTRUMENT_TOKENS

class DataFeed:
    def __init__(self, tick_queue):
        self.kws = KiteTicker(KITE_API_KEY, KITE_ACCESS_TOKEN)
        self.tick_queue = tick_queue
        
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
        logging.info("Successfully connected to Kite WebSocket")
        ws.subscribe(INSTRUMENT_TOKENS)
        ws.set_mode(ws.MODE_FULL, INSTRUMENT_TOKENS)

    def on_close(self, ws, code, reason):
        logging.warning(f"WebSocket closed: {code} - {reason}")

    def on_error(self, ws, code, reason):
        logging.error(f"WebSocket error: {code} - {reason}")

    def start(self):
        # threaded=True runs the websocket in a background thread
        self.kws.connect(threaded=True)
        
    def stop(self):
        self.kws.close()
